"""
Integration tests for the complete mutant generation pipeline
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestIntegration:
    """Integration tests for the complete system"""
    
    def test_complete_mutation_workflow(self, temp_dir, mutation_parser, mutation_applier):
        """Test the complete workflow from parsing to mutation application"""
        # Create a mock project structure
        project_dir = temp_dir / "mock_project"
        project_dir.mkdir()
        
        # Create source structure
        src_dir = project_dir / "src" / "main" / "java" / "org" / "example"
        src_dir.mkdir(parents=True)
        
        # Create a simple Java file
        java_file = src_dir / "Calculator.java"
        java_content = """package org.example;

                            public class Calculator {
                                public int add(int a, int b) {
                                    return a + b;
                                }
                                
                                public boolean isPositive(int x) {
                                    return x > 0;
                                }
                            }
                        """
        java_file.write_text(java_content)
        
        # Create a mock mutants.log - FIXED FORMAT
        mutants_log = project_dir / "mutants.log"
        mutants_content = """# This is a comment line
1:MATH:org.example.Calculator.add(II)I:org.example.Calculator.add(II)I:org.example.Calculator@add:3:45:return a + b |==> return a - b
2:CONDITIONALS_BOUNDARY:org.example.Calculator.isPositive(I)Z:org.example.Calculator.isPositive(I)Z:org.example.Calculator@isPositive:7:342:return x > 0 |==> return x >= 0
"""
        mutants_log.write_text(mutants_content)
        
        print(f"Created mutants.log at: {mutants_log}")
        print(f"Content: {mutants_content}")
        
        # Parse mutations
        mutations = mutation_parser.parse_all_mutations(mutants_log)
        print(f"Parsed mutations: {len(mutations)}")
        for i, mut in enumerate(mutations):
            print(f"Mutation {i}: {mut}")
        
        assert len(mutations) == 2, f"Expected 2 mutations, got {len(mutations)}"
        
        # Generate mutants
        mutants = mutation_applier.generate_unique_mutants(mutations, 2, 1)
        assert len(mutants) == 2
        
        # Create mutant copy
        mutant_dir = temp_dir / "mutant_1"
        success = mutation_applier.create_project_copy(project_dir, mutant_dir)
        assert success is True
        assert mutant_dir.exists()
        
        # Apply mutation to the copy
        mutant_java_file = mutant_dir / "src" / "main" / "java" / "org" / "example" / "Calculator.java"
        mutation = mutants[0]['mutations'][0]
        
        print(f"Applying mutation: line {mutation['line_number']}, '{mutation['original_code']}' -> '{mutation['mutated_code']}'")
        
        success = mutation_applier.apply_mutation_to_file(
            mutant_java_file,
            mutation['line_number'],
            mutation['original_code'],
            mutation['mutated_code']
        )
        
        assert success is True
        
        # Verify mutation was applied
        with open(mutant_java_file, 'r') as f:
            mutant_content = f.read()
        
        print("Original file should have 'return a + b', mutant should have mutation")
        print(f"Mutant content contains 'return a - b': {'return a - b' in mutant_content}")
        
        # The original file should have "return a + b", mutant should have the mutation
        assert "return a + b" in java_content
        # The mutant should either not have the original or have the mutation
        assert "return a + b" not in mutant_content or "return a - b" in mutant_content
    
    def test_parallel_worker_integration(self, temp_dir):
        """Test that parallel worker setup works correctly"""
        from parallel.worker_pool import WorkerPool
        
        worker_pool = WorkerPool(max_workers=2)
        
        # This is a basic test to ensure the worker pool can be instantiated
        # Actual parallel execution testing would require more complex setup
        assert worker_pool.max_workers == 2
        
    def test_configuration_loading(self):
        """Test that configuration is loaded correctly"""
        from config.settings import BASE_CHECKOUT_DIR, MAX_WORKERS, DEFECTS4J_EXECUTABLE
        
        # Basic validation that configuration values exist
        assert BASE_CHECKOUT_DIR is not None
        assert isinstance(MAX_WORKERS, int)
        assert MAX_WORKERS > 0
        assert DEFECTS4J_EXECUTABLE is not None