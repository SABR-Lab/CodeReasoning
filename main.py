#!/usr/bin/env python3
"""
Defects4J Parallel Mutant Generator - JSON OUTPUT
ISOLATED & REPRODUCIBLE across all platforms
"""

import argparse
import sys
import os
import random
import platform
from pathlib import Path

# OVERRIDE: Force use of home directory to avoid macOS permissions
BASE_CHECKOUT_DIR = Path.home() / "defects4j_mutants_testingnewcode"
BASE_CHECKOUT_DIR.mkdir(exist_ok=True)

# Add the parent directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config.settings import BUGS_TO_PROCESS, MAX_WORKERS, DEFAULT_MUTANT_PERCENTAGE, DEFAULT_MAX_MUTATIONS
from core.project_manager import ProjectManager
from core.mutation_parser import MutationParser
from core.mutation_applier import MutationApplier
from parallel.worker_pool import WorkerPool
from utils.json_generator import JSONGenerator
from utils.file_ops import FileOperations


class MutantGenerator:
    """Main orchestrator - REPRODUCIBLE & ISOLATED"""
    
    def __init__(self, max_workers: int = MAX_WORKERS, random_seed: int = 42):
        self.max_workers = max_workers
        self.random_seed = random_seed
        
        # CRITICAL FIX: Only set hash seed for Python, not for subprocesses
        # We'll handle this differently - NOT setting it globally
        
        # Initialize components
        self.project_manager = ProjectManager()
        self.mutation_parser = MutationParser()
        self.json_generator = JSONGenerator()
        self.file_ops = FileOperations()
        
        # Initialize random - but don't affect subprocesses
        random.seed(random_seed)
    
    def process_single_bug(self, project_id: str, bug_id: str,
                          mutant_percentage: int, max_mutations: int) -> bool:
        """Process bug with ISOLATION and REPRODUCIBILITY"""
        
        # CLEANUP any previous runs for THIS bug only
        self._cleanup_bug_directories(project_id, bug_id)
        
        # Create ISOLATED directories
        work_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}f"
        mutants_output_dir = BASE_CHECKOUT_DIR / f"{project_id}_{bug_id}_mutants"
        
        print(f"\n{'='*60}")
        print(f"ISOLATED PROCESS: {project_id}-{bug_id}")
        print(f"Seed: {self.random_seed}")
        print(f"Directory: {work_dir}")
        print(f"Output: {mutants_output_dir}")
        print(f"{'='*60}")
        
        try:
            # Setup project
            if not self._setup_project(project_id, bug_id, work_dir):
                return False
            
            # Get source directories
            source_dirs = self.project_manager.get_source_directories(work_dir)
            if not source_dirs:
                print("✗ No source directories found")
                return False
            
            relative_source_dirs = self.file_ops.get_relative_paths(source_dirs, work_dir)
            
            # Get mutations with PROJECT-SPECIFIC seed
            mutation_applier = MutationApplier(
                random_seed=self.random_seed,
                project_id=project_id,
                bug_id=bug_id
            )
            
            mutations = self._select_mutations(work_dir, mutation_applier, 
                                             mutant_percentage, max_mutations)
            if not mutations:
                return False
            
            # Process with isolation
            worker_pool = WorkerPool(max_workers=self.max_workers)
            successful_mutants, failed_mutants = worker_pool.process_mutants_parallel(
                work_dir, mutants_output_dir, mutations, 
                project_id, bug_id, relative_source_dirs
            )
            
            if successful_mutants:
                # VERIFY all mutants belong to this bug
                verified_mutants = [
                    m for m in successful_mutants 
                    if m.get('project_id') == project_id and m.get('bug_id') == bug_id
                ]
                
                if len(verified_mutants) != len(successful_mutants):
                    print(f"WARNING: {len(successful_mutants) - len(verified_mutants)} "
                          f"mutants had incorrect project/bug tags!")
                
                self._generate_json_results(verified_mutants, mutants_output_dir, 
                                          project_id, bug_id)
                
                print(f"✓ Successfully processed {project_id}-{bug_id}: {len(verified_mutants)} mutants")
                return True
            
            print("✗ No mutants created successfully")
            return False
            
        except Exception as e:
            print(f"ERROR in {project_id}-{bug_id}: {e}")
            import traceback
            traceback.print_exc()
            # Emergency cleanup for this bug only
            self._cleanup_bug_directories(project_id, bug_id)
            return False
    
    # ... rest of the class methods remain the same ...
    
    def _cleanup_bug_directories(self, project_id: str, bug_id: str):
        """Clean up ONLY directories for this specific bug"""
        import shutil
        
        patterns = [
            f"{project_id}_{bug_id}f",
            f"{project_id}_{bug_id}_mutants",
            f"temp_mutant_{project_id}_{bug_id}_*"
        ]
        
        for pattern in patterns:
            for item in BASE_CHECKOUT_DIR.glob(pattern):
                try:
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink(missing_ok=True)
                except:
                    pass
    
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
    
    def _select_mutations(self, work_dir: Path, mutation_applier: MutationApplier,
                         mutant_percentage: int, max_mutations: int) -> list:
        """Select mutations with project-specific isolation"""
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
        
        # Use the project-specific applier
        selected_mutants = mutation_applier.generate_unique_mutants(
            all_mutations, num_mutants, max_mutations
        )
        
        print(f"Generated {len(selected_mutants)} unique mutant combinations")
        return selected_mutants
    
    def _generate_json_results(self, successful_mutants: list, output_dir: Path, 
                             project_id: str, bug_id: str) -> None:
        """Generate JSON results"""
        self.file_ops.ensure_directory(output_dir)
        
        # Create comprehensive JSON
        json_file = output_dir / f"{project_id}_{bug_id}_mutant_coverage.json"
        self.json_generator.create_comprehensive_json(
            successful_mutants, json_file, project_id, bug_id
        )
    
    def merge_project_results(self, project_name: str) -> None:
        """Merge all JSON files for a project"""
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


def check_environment():
    """Environment check"""
    system = platform.system().lower()
    print(f"Platform: {platform.platform()}")
    print(f"Python: {sys.version}")
    
    # Check Defects4J
    try:
        import subprocess
        if system == "windows":
            result = subprocess.run(["defects4j.bat", "version"], capture_output=True, text=True)
        else:
            result = subprocess.run(["defects4j", "version"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Defects4J is available")
        else:
            print("⚠️ Defects4J found but returned error")
    except:
        print("⚠️ Defects4J command not found or error")
    
    return True


def main():
    """Main entry point"""
    # Environment check
    if not check_environment():
        print("Environment check failed. Please fix issues before proceeding.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Defects4J Parallel Mutant Generator - ISOLATED & REPRODUCIBLE",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--project", 
        type=str,
        required=True,
        help='Project(s) to process (e.g., "Math-all", "Math-1", "Math-1,Math-2")'
    )
    
    parser.add_argument(
        "--percentage", 
        type=float,
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
    
    print("Defects4J Parallel Mutant Generator - ISOLATED & REPRODUCIBLE")
    print("=" * 60)
    print(f"Platform: {platform.platform()}")
    print(f"Projects: {len(projects_to_process)}")
    print(f"Mutant Percentage: {args.percentage}%")
    print(f"Max Mutations: {args.max_mutations}")
    print(f"Random Seed: {args.seed}")
    print(f"Workers: {args.workers}")
    print(f"Output: {BASE_CHECKOUT_DIR}")
    print(f"Output Format: JSON")
    print(f"Features: Isolation ✓ | Cross-platform reproducibility ✓")
    print("=" * 60)
    
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
            print(f"\nMerging JSON results for {previous_project}...")
            generator.merge_project_results(previous_project)
        
        success = generator.process_single_bug(project_id, bug_id, args.percentage, args.max_mutations)
        if success:
            success_count += 1
        
        previous_project = project_id
    
    # Merge results for the last project
    if previous_project:
        print(f"\nMerging JSON results for {previous_project}...")
        generator.merge_project_results(previous_project)
    
    print(f"\n{'='*60}")
    print(f"COMPLETED: {success_count}/{len(projects_to_process)} projects processed successfully")
    print(f"Random Seed Used: {args.seed}")
    print(f"Results saved in: {BASE_CHECKOUT_DIR}")
    print(f"Output Format: JSON")


if __name__ == "__main__":
    main()