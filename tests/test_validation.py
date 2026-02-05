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
            {'mutant_id': '1', 'mutator': 'MUTATOR1', 'l':'l','l':'l','class_name': 'Test', 
             'line_number': 10, 'j':34,'original_code': 'code1', 'mutated_code': 'mut1'},
            {'mutant_id': '2', 'mutator': 'MUTATOR2','l':'l','l':'l', 'class_name': 'Test', 
             'line_number': 15, 'j':34,'original_code': 'code2', 'mutated_code': 'mut2'},
            {'mutant_id': '3', 'mutator': 'MUTATOR3','l':'l','l':'l', 'class_name': 'Test', 
             'line_number': 20, 'j':34,'original_code': 'code3', 'mutated_code': 'mut3'},
        ]
        
        # Generate mutants with same seed
        applier1 = MutationApplier(random_seed=42)
        mutants1 = applier1.generate_unique_mutants(sample_mutations, 2, 2)
        
        applier2 = MutationApplier(random_seed=42) 
        mutants2 = applier2.generate_unique_mutants(sample_mutations, 2, 2)
        
        # Should be identical
        assert len(mutants1) == len(mutants2)
        #assert mutants1[0]['signature'] == mutants2[0]['signature']
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
        """Validate JSON generation produces correct format"""
        import json
        from utils.json_generator import JSONGenerator
        
        # 1. Setup: Create the input data expected by create_comprehensive_json
        # The generator expects a list of dictionaries, not a nested dict
        sample_mutants = [
            {
                'mutant_id': 'mutant_1',
                'mutator': 'MathMutator',
                'class_name': 'org.example.Math',
                'line_number': '42',
                'target_file': 'src/main/java/Math.java',
                'num_mutations': 1,
                'mutation_signature': 'sig123',
                'coverage_percentage': 85.5,
                'branch_coverage': 70.0,
                'total_tests_count': 50,
                'failed_test_count': 1,
                'coverage_success': True,
                'failed_tests': ['test_fail_1'],
                'all_tests': ['test_fail_1', 'test_pass_1'],
                'method_coverage': {
                    'void test()': ['42', '43']
                }
            }
        ]
        
        # 2. Execution: Generate the file
        generator = JSONGenerator()
        output_file = temp_dir / "test_output.json"
        
        generator.create_comprehensive_json(
            sample_mutants, output_file, "Math", "1"
        )
        
        # 3. Verification: Read the generated file and check structure
        assert output_file.exists()
        
        with open(output_file, 'r') as f:
            generated_data = json.load(f)
            
        # Check Root Metadata
        assert "metadata" in generated_data
        assert generated_data["metadata"]["project"] == "Math"
        assert generated_data["metadata"]["bug_id"] == "1"
        assert generated_data["metadata"]["total_mutants"] == 1
        
        # Check Mutants List
        assert "mutants" in generated_data
        assert isinstance(generated_data["mutants"], list)
        assert len(generated_data["mutants"]) == 1
        
        # Check Specific Mutant Fields
        mutant = generated_data["mutants"][0]
        assert mutant["mutant_id"] == "mutant_1"
        
        # Check Nested Structures (Coverage)
        assert "coverage" in mutant
        assert mutant["coverage"]["line_coverage_percentage"] == 85.5
        assert mutant["coverage"]["coverage_success"] is True
        
        # Check Nested Structures (Tests)
        assert "tests" in mutant
        assert "failed_tests" in mutant["tests"]
        assert "all_tests" in mutant["tests"]
        assert mutant["tests"]["failed_tests"] == ['test_fail_1']
        
        # Check Nested Structures (Method Coverage)
        assert "method_coverage" in mutant
        assert mutant["method_coverage"] == {'void test()': ['42', '43']}