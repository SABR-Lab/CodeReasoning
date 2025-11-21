"""Handles CSV file generation and merging"""

import csv
from pathlib import Path
from typing import List, Dict, Set


class CSVGenerator:
    """Generates and merges CSV files with coverage data"""
    
    @staticmethod
    def create_comprehensive_coverage_csv(successful_mutants: List[Dict], csv_file_path: Path, 
                                        project_id: str, bug_id: str) -> None:
        """Create a comprehensive CSV file with test results and coverage information"""
        print(f"Creating comprehensive coverage CSV: {csv_file_path}")
        
        # Collect all unique methods across all mutants
        all_methods: Set[str] = set()
        for mutant in successful_mutants:
            all_methods.update(mutant['method_coverage'].keys())
        
        sorted_methods = sorted(all_methods)
        
        # Define standard columns
        standard_columns = [
            'Mutant', 'Line Coverage %', 'Mutator', 'Class Name', 
            'Line Number', 'Target File', 'Total Tests Count', 
            'Failed Test Count', 'Failed Tests', 'All Tests'
        ]
        
        with open(csv_file_path, 'w', newline='') as csvfile:
            # Create header with standard columns + method columns
            fieldnames = standard_columns + sorted_methods
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write data rows
            for mutant in successful_mutants:
                row_data = {
                    'Mutant': f"{project_id}_{bug_id}_mutant_{mutant['mutant_id']}",
                    'Line Coverage %': f"{mutant['coverage_percentage']:.2f}",
                    'Mutator': mutant['mutator'],
                    'Class Name': mutant['class_name'],
                    'Line Number': mutant['line_number'],
                    'Target File': mutant['target_file'],
                    'Total Tests Count': mutant['total_tests_count'],
                    'Failed Test Count': mutant['failed_test_count'],
                    'Failed Tests': '; '.join(mutant['failed_tests']),
                    'All Tests': '; '.join(mutant['all_tests'])
                }
                
                # Add method coverage data
                for method in sorted_methods:
                    line_numbers = mutant['method_coverage'].get(method, [])
                    row_data[method] = ','.join(line_numbers)
                
                writer.writerow(row_data)
        
        print(f"Created CSV with {len(successful_mutants)} entries and {len(sorted_methods)} methods")
    
    @staticmethod
    def merge_project_csv_files(project_name: str, base_dir: Path) -> Path:
        """Merge all CSV files for a project into a single master file"""
        print(f"\nMerging CSV files for project: {project_name}")
        
        merged_csv_path = base_dir / f"{project_name}_All_Bugs_Merged.csv"
        
        # Find all CSV files for the project
        csv_files = list(base_dir.rglob(f"{project_name}_*_coverage.csv"))
        
        if not csv_files:
            print("No CSV files found to merge")
            return None
        
        print(f"Found {len(csv_files)} CSV files")
        
        # Collect all unique headers
        master_fieldnames: Set[str] = set()
        standard_columns = [
            'Mutant', 'Line Coverage %', 'Mutator', 'Class Name', 
            'Line Number', 'Target File', 'Total Tests Count', 
            'Failed Test Count', 'Failed Tests', 'All Tests'
        ]
        
        for csv_path in csv_files:
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames:
                        master_fieldnames.update(reader.fieldnames)
            except Exception as e:
                print(f"Warning: Could not read {csv_path.name}: {e}")
        
        # Organize headers: standard columns first, then dynamic method columns
        dynamic_columns = sorted([f for f in master_fieldnames if f not in standard_columns])
        final_header = standard_columns + dynamic_columns
        
        print(f"Total unique columns: {len(final_header)}")
        
        # Merge all data
        total_rows = 0
        try:
            with open(merged_csv_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=final_header, extrasaction='ignore')
                writer.writeheader()
                
                for csv_path in csv_files:
                    with open(csv_path, 'r', encoding='utf-8') as infile:
                        reader = csv.DictReader(infile)
                        rows_written = 0
                        for row in reader:
                            writer.writerow(row)
                            rows_written += 1
                            total_rows += 1
                    
                    print(f"  Merged {rows_written} rows from {csv_path.name}")
            
            print(f"✓ Successfully merged {total_rows} rows from {len(csv_files)} files")
            print(f"  Master CSV: {merged_csv_path}")
            return merged_csv_path
            
        except Exception as e:
            print(f"✗ Error during merging: {e}")
            return None