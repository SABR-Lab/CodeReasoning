"""
Validation tests for the mutant generator
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from core.mutation_applier import MutationApplier


class TestValidation:
    """Validation tests for the overall system"""
    
    def test_mutation_parsing_validation(self, mutation_parser, sample_mutations_log_file):
        """Validate that mutation parsing produces consistent results"""
        # Parse multiple times should give same results
        mutations1 = mutation_parser.parse_all_mutations(sample_mutations_log_file)
        mutations2 = mutation_parser.parse_all_mutations(sample_mutations_log_file)
        
        assert len(mutations1) == len(mutations2)
        assert mutations1[0]['mutant_id'] == mutations2[0]['mutant_id']
        assert mutations1[0]['original_code'] == mutations2[0]['original_code']
    
    def test_mutant_generation_reproducibility(self, mutation_applier):
        """Validate that mutant generation is reproducible with same seed"""
        sample_mutations = [
            {'mutant_id': '1', 'mutator': 'MUTATOR1', 'class_name': 'Test', 
             'line_number': 10, 'original_code': 'code1', 'mutated_code': 'mut1'},
            {'mutant_id': '2', 'mutator': 'MUTATOR2', 'class_name': 'Test', 
             'line_number': 15, 'original_code': 'code2', 'mutated_code': 'mut2'},
            {'mutant_id': '3', 'mutator': 'MUTATOR3', 'class_name': 'Test', 
             'line_number': 20, 'original_code': 'code3', 'mutated_code': 'mut3'},
        ]
        
        # Generate mutants with same seed
        applier1 = MutationApplier(random_seed=42)
        mutants1 = applier1.generate_unique_mutants(sample_mutations, 2, 2)
        
        applier2 = MutationApplier(random_seed=42) 
        mutants2 = applier2.generate_unique_mutants(sample_mutations, 2, 2)
        
        # Should be identical
        assert len(mutants1) == len(mutants2)
        assert mutants1[0]['signature'] == mutants2[0]['signature']
        assert mutants1[1]['signature'] == mutants2[1]['signature']
    
    def test_mutant_generation_uniqueness(self, mutation_applier):
        """Validate that generated mutants are unique"""
        sample_mutations = [
            {'mutant_id': '1', 'mutator': 'MUTATOR1', 'class_name': 'Test', 
             'line_number': 10, 'original_code': 'code1', 'mutated_code': 'mut1'},
            {'mutant_id': '2', 'mutator': 'MUTATOR2', 'class_name': 'Test', 
             'line_number': 15, 'original_code': 'code2', 'mutated_code': 'mut2'},
        ]
        
        mutants = mutation_applier.generate_unique_mutants(sample_mutations, 3, 2)
        
        # All mutants should have unique signatures
        signatures = [m['signature'] for m in mutants]
        assert len(signatures) == len(set(signatures))
    
    def test_file_operations_validation(self, temp_dir):
        """Validate file operations work correctly"""
        from utils.file_ops import FileOperations
        
        file_ops = FileOperations()
        
        # Test directory creation
        test_dir = temp_dir / "test_subdir"
        assert file_ops.ensure_directory(test_dir) is True
        assert test_dir.exists()
        
        # Test directory cleaning
        test_file = test_dir / "test.txt"
        test_file.write_text("content")
        assert file_ops.clean_directory(test_dir) is True
        assert not test_dir.exists()
    
    def test_csv_generation_validation(self, temp_dir):
        """Validate CSV generation produces correct format"""
        from utils.json_generator import JSONGenerator
        
        csv_generator = JSONGenerator()
        
        sample_mutants = [
            {
                'mutant_id': '1',
                'mutator': 'VOID_METHOD_CALLS',
                'class_name': 'org.example.Test',
                'line_number': 10,
                'target_file': 'src/Test.java',
                'total_tests_count': 100,
                'failed_test_count': 5,
                'failed_tests': ['test1', 'test2'],
                'all_tests': ['test1', 'test2', 'test3'],
                'coverage_success': True,
                'coverage_percentage': 85.5,
                'method_coverage': {
                    'org.example.Test.method1()V': ['10', '11'],
                    'org.example.Test.method2(I)Z': ['15']
                }
            }
        ]
        
        csv_file = temp_dir / "test_output.csv"
        csv_generator.create_comprehensive_coverage_csv(
            sample_mutants, csv_file, "Math", "1"
        )
        
        assert csv_file.exists()
        
        # Verify CSV has expected columns
        import csv
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            assert 'Mutant' in fieldnames
            assert 'Line Coverage %' in fieldnames
            assert 'Mutator' in fieldnames
            assert 'Class Name' in fieldnames
            assert 'Total Tests Count' in fieldnames
            assert 'org.example.Test.method1()V' in fieldnames