"""Manages parallel execution of mutant tasks"""
import shutil
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Tuple

from config.settings import MAX_WORKERS
from core.mutation_applier import MutationApplier
from core.coverage_runner import CoverageRunner


class WorkerPool:
    """Manages parallel execution of mutant creation and analysis"""
    
    def __init__(self, max_workers: int = MAX_WORKERS):
        self.max_workers = max_workers
        self.mutation_applier = MutationApplier()
        self.coverage_runner = CoverageRunner()
    
    def process_single_mutant(self, args: Tuple) -> Dict[str, Any]:
        """
        Process a single mutant - applies mutation and runs coverage
        This function runs in parallel processes
        """
        work_dir, mutant_dir, mutant_info, project_id, bug_id, relative_source_dirs = args
        
        mutant_id = mutant_info['mutant_id']
        pid = os.getpid()
        
        try:
            print(f"   [Process {pid}] Starting Mutant {mutant_id} with {mutant_info['num_mutations']} mutations...")
            
            # 1. Create project copy
            if not self.mutation_applier.create_project_copy(work_dir, mutant_dir):
                return None
            
            # 2. Reconstruct source directories
            source_dirs = [mutant_dir / rel_path for rel_path in relative_source_dirs]
            
            # 3. Group mutations by file
            mutations_by_file = {}
            for mutation in mutant_info['mutations']:
                class_name = mutation['class_name']
                target_file = self.mutation_applier.find_java_file_by_class(class_name, source_dirs)
                if target_file:
                    if target_file not in mutations_by_file:
                        mutations_by_file[target_file] = []
                    mutations_by_file[target_file].append(mutation)
            
            # 4. Apply mutations to each file
            all_success = True
            for target_file, file_mutations in mutations_by_file.items():
                if len(file_mutations) == 1:
                    # Single mutation
                    mutation = file_mutations[0]
                    success = self.mutation_applier.apply_mutation_to_file(
                        target_file,
                        mutation['line_number'],
                        mutation['original_code'],
                        mutation['mutated_code']
                    )
                else:
                    # Multiple mutations to the same file
                    success = self.mutation_applier.apply_multiple_mutations(target_file, file_mutations)
                
                if not success:
                    all_success = False
                    print(f"   [Process {pid}] Failed to apply mutations to {target_file}")
                    break
            
            if not all_success:
                return None
            
            # 5. Run coverage analysis
            coverage_result = self.coverage_runner.run_coverage_analysis(mutant_dir, project_id, bug_id)
            
            # 6. Prepare result
            # Collect all file paths, classes, and line numbers
            all_target_files = [str(f.relative_to(mutant_dir)) for f in mutations_by_file.keys()]
            # Fix this section - check if class_name is already a string or needs processing
            if isinstance(mutant_info['class_name'], str) and ', ' in mutant_info['class_name']:
                all_classes = mutant_info['class_name'].split(', ')
            else:
                all_classes = [str(mutant_info['class_name'])]  # Ensure it's a list

            # Same fix for line numbers
            if isinstance(mutant_info['line_number'], str) and ', ' in mutant_info['line_number']:
                all_line_numbers = mutant_info['line_number'].split(', ')
            else:
                all_line_numbers = [str(mutant_info['line_number'])]  # Ensure it's a list
            result_info = {
                'mutant_id': mutant_info['mutant_id'],
                'mutant_directory': str(mutant_dir),
                'mutator': mutant_info['mutator'],
                'class_name': ', '.join(all_classes),              # ← All classes
                'line_number': ', '.join(all_line_numbers),        # ← All line numbers
                'target_file': '; '.join(all_target_files),        # ← All target files
                'total_tests_count': coverage_result['total_tests'],
                'failed_test_count': coverage_result['failed_count'],
                'failed_tests': coverage_result['failed_tests'],
                'all_tests': coverage_result['all_tests'],
                'coverage_success': coverage_result['coverage_success'],
                'coverage_percentage': coverage_result['coverage_percentage'],
                'method_coverage': coverage_result['method_coverage'],
                'num_mutations': mutant_info['num_mutations'],
                'mutation_signature': mutant_info['signature']
            }

            # Save coverage output
            coverage_output_file = mutant_dir / "coverage_output.log"
            with open(coverage_output_file, 'w') as f:
                f.write(coverage_result['coverage_output'])
            
            print(f"   [Process {pid}] Finished Mutant {mutant_id} (Cov: {coverage_result['coverage_percentage']:.2f}%, Mutations: {mutant_info['num_mutations']})")
            return result_info

        except Exception as e:
            print(f"   [Process {pid}] Error: {e}")
            return None
        
        finally:
            # Cleanup to save disk space
            if mutant_dir.exists():
                try:
                    shutil.rmtree(mutant_dir)
                except:
                    pass  # Ignore cleanup errors
    
    def process_mutants_parallel(self, work_dir: Path, mutants_output_dir: Path,
                               mutants: List[Dict], project_id: str, bug_id: str,
                               relative_source_dirs: List[Path]) -> Tuple[List[Dict], List[str]]:
        """
        Process multiple mutants in parallel using ProcessPoolExecutor
        """
        successful_mutants = []
        failed_mutations = []
        
        # Prepare arguments for all workers
        worker_args = []
        for mutant_info in mutants:
            mutant_dir = work_dir.parent / f"{project_id}_{bug_id}_{mutant_info['mutant_id']}"
            if mutant_dir.exists():
                shutil.rmtree(mutant_dir)
            
            args = (work_dir, mutant_dir, mutant_info, project_id, bug_id, relative_source_dirs)
            worker_args.append(args)
        
        print(f"Processing {len(mutants)} mutants with {self.max_workers} workers...")
        
        # Execute in parallel
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_mid = {
                executor.submit(self.process_single_mutant, arg): arg[2]['mutant_id'] 
                for arg in worker_args
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_mid):
                mutant_id = future_to_mid[future]
                try:
                    result = future.result()
                    if result:
                        successful_mutants.append(result)
                        print(f"✓ Successfully processed mutant {mutant_id}")
                    else:
                        failed_mutations.append(mutant_id)
                        print(f"✗ Failed to process mutant {mutant_id}")
                except Exception as e:
                    print(f"✗ Worker exception for mutant {mutant_id}: {e}")
                    failed_mutations.append(mutant_id)
        
        print(f"Parallel processing completed: {len(successful_mutants)} successful, {len(failed_mutations)} failed")
        return successful_mutants, failed_mutations