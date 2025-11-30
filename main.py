#!/usr/bin/env python3
"""
Defects4J Parallel Mutant Generator - PLATFORM INDEPENDENT

Cross-platform version that works on Windows, macOS, and Linux.
"""

import argparse
import sys
import os
import random
import platform
from pathlib import Path
#first run in terminal export PATH=$PATH:"/Users/quibliss/research/defects4j_codes/defects4j"/framework/bin
BASE_CHECKOUT_DIR = Path.home() / "defects4j_mutants"
BASE_CHECKOUT_DIR.mkdir(exist_ok=True)
# Add the parent directory to Python path - PLATFORM INDEPENDENT
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config.settings import BUGS_TO_PROCESS, BASE_CHECKOUT_DIR, MAX_WORKERS, DEFAULT_MUTANT_PERCENTAGE, DEFAULT_MAX_MUTATIONS
from core.project_manager import ProjectManager
from core.mutation_parser import MutationParser
from core.mutation_applier import MutationApplier
from parallel.worker_pool import WorkerPool
from utils.json_generator import JSONGenerator
from utils.file_ops import FileOperations


def check_environment():
    """Check if the environment is suitable for execution"""
    system = platform.system().lower()
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    
    # Check if Defects4J is likely available
    try:
        import subprocess
        if system == "windows":
            result = subprocess.run(["defects4j.bat", "env"], capture_output=True, text=True)
        else:
            result = subprocess.run(["defects4j", "env"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Defects4J is available")
        else:
            print("✗ Defects4J may not be properly installed")
            print("Please ensure Defects4J is in your PATH")
    except:
        print("✗ Defects4J command not found")
        print("Please install Defects4J and ensure it's in your PATH")
    
    return True


class MutantGenerator:
    """Main orchestrator for mutant generation process"""
    
    def __init__(self, max_workers: int = MAX_WORKERS, random_seed: int = 42):
        self.max_workers = max_workers
        self.random_seed = random_seed
        self.project_manager = ProjectManager()
        self.mutation_parser = MutationParser()
        self.mutation_applier = MutationApplier(random_seed=random_seed)
        self.worker_pool = WorkerPool(max_workers=max_workers)
        self.json_generator = JSONGenerator()  # CHANGED: Use JSON generator
        self.file_ops = FileOperations()
        
        # Set global random seed for reproducibility
        random.seed(random_seed)
    
    def process_single_bug(self, project_id: str, bug_id: str, 
                          mutant_percentage: int, max_mutations: int) -> bool:
        """Process a single project bug and generate mutants"""
        work_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}f"
        mutants_output_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}_mutants"
        
        print(f"\nProcessing: {project_id}-{bug_id}")
        print(f"Mutant Percentage: {mutant_percentage}%")
        print(f"Max Mutations: {max_mutations}")
        print(f"Random Seed: {self.random_seed}")
        print("=" * 50)
        
        try:
            # Step 1: Setup project
            if not self._setup_project(project_id, bug_id, work_dir):
                return False
            
            # Step 2: Get source directories
            source_dirs = self.project_manager.get_source_directories(work_dir)
            if not source_dirs:
                print("✗ No source directories found")
                return False
            
            relative_source_dirs = self.file_ops.get_relative_paths(source_dirs, work_dir)
            
            # Step 3: Parse mutations and select based on percentage and max mutations
            mutations = self._select_mutations(work_dir, mutant_percentage, max_mutations)
            if not mutations:
                return False
            
            # Step 4: Process mutants in parallel
            successful_mutants, failed_mutations = self.worker_pool.process_mutants_parallel(
                work_dir, mutants_output_dir, mutations, project_id, bug_id, relative_source_dirs
            )
            
            if not successful_mutants:
                print("✗ No mutants created successfully")
                return False
            
            # Step 5: Generate JSON results (CHANGED: from CSV to JSON)
            self._generate_json_results(successful_mutants, mutants_output_dir, project_id, bug_id)
            
            print(f"✓ Successfully processed {project_id}-{bug_id}: {len(successful_mutants)} mutants")
            return True
            
        except Exception as e:
            print(f"✗ Error processing {project_id}-{bug_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_project(self, project_id: str, bug_id: str, work_dir: Path) -> bool:
        """Setup project: checkout, compile, run mutation testing"""
        # Clean existing directories
        self.file_ops.clean_directory(work_dir)
        
        # Checkout and compile
        if not self.project_manager.checkout_project(project_id, bug_id, work_dir):
            return False
        
        # Run mutation testing
        if not self.project_manager.run_mutation_testing(work_dir):
            return False
        
        return True
    
    def _select_mutations(self, work_dir: Path, mutant_percentage: int, max_mutations: int) -> list:
        """Parse mutations and select based on percentage and max mutations constraint"""
        log_file = self.mutation_parser.find_mutants_log(work_dir)
        if not log_file:
            print("✗ No mutants.log found")
            return []
        
        all_mutations = self.mutation_parser.parse_all_mutations(log_file)
        if not all_mutations:
            print("✗ No mutations parsed")
            return []
        
        # Calculate number of mutants based on percentage
        num_mutants = max(1, int(len(all_mutations) * mutant_percentage / 100))
        print(f"Total mutations available: {len(all_mutations)}")
        print(f"Creating {num_mutants} mutants ({mutant_percentage}%)")
        
        # Generate unique mutant combinations
        selected_mutants = self.mutation_applier.generate_unique_mutants(
            all_mutations, num_mutants, max_mutations
        )
        
        print(f"Generated {len(selected_mutants)} unique mutant combinations")
        return selected_mutants
    
    def _generate_json_results(self, successful_mutants: list, output_dir: Path, 
                             project_id: str, bug_id: str) -> None:
        """Generate JSON results (CHANGED: from CSV to JSON)"""
        self.file_ops.ensure_directory(output_dir)
        
        # Create comprehensive JSON
        json_file = output_dir / f"{project_id}_{bug_id}_mutant_coverage.json"  # CHANGED: .json extension
        self.json_generator.create_comprehensive_json(
            successful_mutants, json_file, project_id, bug_id
        )
    
    def merge_project_results(self, project_name: str) -> None:
        """Merge all JSON files for a project (CHANGED: from CSV to JSON)"""
        self.json_generator.merge_project_json_files(project_name, BASE_CHECKOUT_DIR)

def parse_project_argument(project_arg: str) -> list:
    """Parse project argument like 'Math-all', 'Math-1', 'Math-1,Math-2'"""
    if not project_arg:
        return []
    
    projects_to_process = []
    
    for item in project_arg.split(','):
        item = item.strip()
        if '-' in item:
            project, bug = item.split('-', 1)
            project = project.strip()
            bug = bug.strip()
            
            if bug.lower() == 'all':
                # Add all bugs for this project
                for proj, bug_id in BUGS_TO_PROCESS:
                    if proj == project:
                        projects_to_process.append((proj, bug_id))
            else:
                projects_to_process.append((project, bug))
    
    return projects_to_process


def validate_arguments(percentage: int, max_mutations: int) -> bool:
    """Validate input arguments"""
    if not (0 <= percentage <= 100):
        print("Error: Percentage must be between 0 and 100")
        return False
    
    if not (1 <= max_mutations <= 4):
        print("Error: Max mutations must be between 1 and 4")
        return False
    
    return True

def main():
    """Main entry point - PLATFORM INDEPENDENT"""
    # Environment check
    if not check_environment():
        print("Environment check failed. Please fix issues before proceeding.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Defects4J Parallel Mutant Generator - PLATFORM INDEPENDENT",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # ... (argument parsing remains the same)
    print("Projects: \"Math(1-106)", "Lang(1-65)", "Time(1-27)", "Chart(1-26)", "Closure(1-194)", "Codec(1-18)", 
           "Compress(1-47)", "Csv(1-16)", "JacksonCore(1-26)", "JacksonDatabind(1-113)", 
           "JacksonXml(1-6)", "Jsoup(1-93)", "JxPath(1-22)\"")
    
    parser.add_argument(
        "--project", 
        type=str,
        required=True,
        help='Project(s) to process (e.g., "Math-all", "Math-1", "Math-1,Math-2")'
    )
    
    parser.add_argument(
        "--percentage", 
        type=int,
        default=DEFAULT_MUTANT_PERCENTAGE,
        help=f"Percentage of mutants to create (0-100, default: {DEFAULT_MUTANT_PERCENTAGE})"
    )
    
    parser.add_argument(
        "--max-mutations", 
        type=int,
        default=DEFAULT_MAX_MUTATIONS,
        help=f"Maximum number of mutations per mutant (1-4, default: {DEFAULT_MAX_MUTATIONS})"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=MAX_WORKERS,
        help=f"Number of parallel workers (default: {MAX_WORKERS})"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible mutant selection (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not validate_arguments(args.percentage, args.max_mutations):
        sys.exit(1)
    
    # Parse project argument
    projects_to_process = parse_project_argument(args.project)
    
    if not projects_to_process:
        print("Error: No valid projects found to process")
        print("Available formats: 'Math-all', 'Math-1', 'Math-1,Math-2'")
        sys.exit(1)

    print("Defects4J Parallel Mutant Generator - PLATFORM INDEPENDENT")
    print("=" * 60)
    print(f"Platform: {platform.platform()}")
    print(f"Projects: {len(projects_to_process)}")
    print(f"Mutant Percentage: {args.percentage}%")
    print(f"Max Mutations: {args.max_mutations}")
    print(f"Random Seed: {args.seed}")
    print(f"Workers: {args.workers}")
    print(f"Output: {BASE_CHECKOUT_DIR}")
    print("=" * 60)
    
    # Rest of main function remains the same...
    # Set global random seed immediately
    random.seed(args.seed)
    
    # Initialize generator with seed
    generator = MutantGenerator(max_workers=args.workers, random_seed=args.seed)
    
    # Process all projects
    success_count = 0
    previous_project = None
    
    for project_id, bug_id in projects_to_process:
        # Merge previous project results when switching projects
        if previous_project and previous_project != project_id:
            print(f"\nMerging results for {previous_project}...")
            generator.merge_project_results(previous_project)
        
        success = generator.process_single_bug(project_id, bug_id, args.percentage, args.max_mutations)
        if success:
            success_count += 1
        
        previous_project = project_id
    
    # Merge results for the last project
    if previous_project:
        print(f"\nMerging results for {previous_project}...")
        generator.merge_project_results(previous_project)
    
    print(f"\n{'='*60}")
    print(f"COMPLETED: {success_count}/{len(projects_to_process)} projects processed successfully")
    print(f"Random Seed Used: {args.seed}")
    print(f"Results saved in: {BASE_CHECKOUT_DIR}")

if __name__ == "__main__":
    main()