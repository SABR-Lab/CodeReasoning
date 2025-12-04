"""Handles JSON file generation for mutant results"""

import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

class JSONGenerator:
    """Generates JSON files with coverage and mutation data"""
    
    @staticmethod
    def create_comprehensive_json(successful_mutants: List[Dict], json_file_path: Path, 
                                project_id: str, bug_id: str) -> None:
        """Create a comprehensive JSON file with test results and coverage information"""
        print(f"Creating comprehensive JSON: {json_file_path}")
        
        # Prepare the JSON structure
        json_data = {
            'metadata': {
                'project': project_id,
                'bug_id': bug_id,
                'timestamp': datetime.now().isoformat(),
                'total_mutants': len(successful_mutants),
                'mutants_processed': len(successful_mutants)
            },
            'mutants': []
        }
        
        # Add each mutant's data
        for mutant in successful_mutants:
            mutant_data = {
                'mutant_id': mutant['mutant_id'],
                'mutator': mutant['mutator'],
                'class_name': mutant['class_name'],
                'line_number': mutant['line_number'],
                'target_file': mutant['target_file'],
                'num_mutations': mutant.get('num_mutations', 1),
                'mutation_signature': mutant.get('mutation_signature', ''),
                'coverage': {
                    'line_coverage_percentage': mutant['coverage_percentage'],
                    'total_tests_count': mutant['total_tests_count'],
                    'failed_test_count': mutant['failed_test_count'],
                    'coverage_success': mutant['coverage_success']
                },
                'tests': {
                    'failed_tests': mutant['failed_tests'],
                    'all_tests': mutant['all_tests']
                },
                'method_coverage': mutant['method_coverage']
            }
            json_data['mutants'].append(mutant_data)
        
        # Write JSON file
        with open(json_file_path, 'w') as jsonfile:
            json.dump(json_data, jsonfile, indent=2)
        
        print(f"Created JSON with {len(successful_mutants)} mutants")
    
    @staticmethod
    def merge_project_json_files(project_name: str, base_dir: Path) -> Path:
        """Merge all JSON files for a project into a single master JSON file"""
        print(f"\nMerging JSON files for project: {project_name}")
        
        merged_json_path = base_dir / f"{project_name}_All_Bugs_Merged.json"
        
        # Find all JSON files for the project
        json_files = list(base_dir.rglob(f"{project_name}_*_mutant_coverage.json"))
        
        if not json_files:
            print("No JSON files found to merge")
            return None
        
        print(f"Found {len(json_files)} JSON files")
        
        # Prepare merged JSON structure
        merged_data = {
            'metadata': {
                'project': project_name,
                'timestamp': datetime.now().isoformat(),
                'total_bugs': len(json_files),
                'bugs_processed': []
            },
            'bugs': {}
        }
        
        total_mutants = 0
        
        # Merge data from all JSON files
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    bug_data = json.load(f)
                
                # Extract bug ID from filename (e.g., "Math_4_mutant_coverage.json" -> "4")
                bug_id = json_file.stem.replace(f"{project_name}_", "").replace("_mutant_coverage", "")
                
                # Add to merged data
                merged_data['bugs'][bug_id] = bug_data
                merged_data['metadata']['bugs_processed'].append(bug_id)
                total_mutants += len(bug_data.get('mutants', []))
                
                print(f"  Merged data from {json_file.name} - {len(bug_data.get('mutants', []))} mutants")
                
            except Exception as e:
                print(f"  Error reading {json_file.name}: {e}")
        
        merged_data['metadata']['total_mutants'] = total_mutants
        
        # Write merged JSON file
        try:
            with open(merged_json_path, 'w', encoding='utf-8') as outfile:
                json.dump(merged_data, outfile, indent=2, ensure_ascii=False)
            
            print(f"✓ Successfully merged {total_mutants} mutants from {len(json_files)} bugs")
            print(f"  Master JSON: {merged_json_path}")
            return merged_json_path
            
        except Exception as e:
            print(f"✗ Error during JSON merging: {e}")
            return None
    
    @staticmethod
    def create_summary_json(project_data: Dict, output_dir: Path) -> None:
        """Create a summary JSON file with high-level statistics"""
        summary_data = {
            'summary': {
                'total_projects': len(project_data),
                'total_mutants': sum(data.get('total_mutants', 0) for data in project_data.values()),
                'generation_date': datetime.now().isoformat()
            },
            'projects': project_data
        }
        
        summary_path = output_dir / "experiment_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"Created summary JSON: {summary_path}")