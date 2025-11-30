"""
Tests for mutation parsing functionality
"""

import pytest
from pathlib import Path


class TestMutationParser:
    """Test MutationParser class"""
    
    def test_parse_mutant_line_valid(self, mutation_parser):
        """Test parsing a valid mutant line"""
        line = "1:VOID_METHOD_CALLS:org.example.Test.voidMethod()V:org.example.Test.voidMethod()V:org.example.Test@testMethod:10:someObject.voidMethod() |==> "
        
        result = mutation_parser.parse_mutant_line(line)
        
        assert result is not None
        assert result['mutant_id'] == '1'
        assert result['mutator'] == 'VOID_METHOD_CALLS'
        assert result['class_name'] == 'org.example.Test'
        assert result['line_number'] == 10
        assert result['original_code'] == 'someObject.voidMethod()'
        assert result['mutated_code'] == ''
    
    def test_parse_mutant_line_with_mutation(self, mutation_parser):
        """Test parsing a line with actual mutation"""
        line = "2:CONDITIONALS_BOUNDARY:org.example.Test.test(I)Z:org.example.Test.test(I)Z:org.example.Test@test:15:x > 0 |==> x >= 0"
        
        result = mutation_parser.parse_mutant_line(line)
        
        assert result is not None
        assert result['mutant_id'] == '2'
        assert result['mutator'] == 'CONDITIONALS_BOUNDARY'
        assert result['original_code'] == 'x > 0'
        assert result['mutated_code'] == 'x >= 0'
    
    def test_parse_mutant_line_invalid(self, mutation_parser):
        """Test parsing invalid lines"""
        # Empty line
        assert mutation_parser.parse_mutant_line('') is None
        
        # Comment line
        assert mutation_parser.parse_mutant_line('# This is a comment') is None
        
        # Malformed line
        assert mutation_parser.parse_mutant_line('incomplete:line') is None
        
        # Line with insufficient parts
        assert mutation_parser.parse_mutant_line('1:VOID_METHOD_CALLS:only:three:parts') is None
    
    def test_parse_mutant_line_no_op(self, mutation_parser):
        """Test parsing NO-OP mutation"""
        line = "3:VOID_METHOD_CALLS:org.example.Test.method()V:org.example.Test.method()V:org.example.Test@method:10:call() |==> <NO-OP>"
        
        result = mutation_parser.parse_mutant_line(line)
        
        assert result is not None
        assert result['mutated_code'] == '/*' + result['original_code'] + '*/'
    
    def test_find_mutants_log(self, temp_dir, mutation_parser):
        """Test finding mutants.log file"""
        # Create a mock project structure
        project_dir = temp_dir / "Math_1f"
        project_dir.mkdir()
        
        # Test when mutants.log exists
        log_file = project_dir / "mutants.log"
        log_file.write_text("test content")
        
        found_log = mutation_parser.find_mutants_log(project_dir)
        assert found_log == log_file
        
        # Test when mutants.log doesn't exist
        no_log_dir = temp_dir / "NoLogDir"
        no_log_dir.mkdir()
        
        found_log = mutation_parser.find_mutants_log(no_log_dir)
        assert found_log is None
    
    def test_parse_all_mutations(self, mutation_parser, sample_mutations_log_file):
        """Test parsing all mutations from a log file"""
        mutations = mutation_parser.parse_all_mutations(sample_mutations_log_file)
        
        assert len(mutations) == 4
        assert mutations[0]['mutant_id'] == '1'
        assert mutations[1]['mutant_id'] == '2'
        assert mutations[2]['mutant_id'] == '3'
        assert mutations[3]['mutant_id'] == '4'
    
    def test_parse_all_mutations_duplicate_filtering(self, mutation_parser, temp_dir):
        """Test that duplicate mutations are filtered out"""
        log_content = """1:VOID_METHOD_CALLS:org.example.Test@method:10:code |==> 
1:VOID_METHOD_CALLS:org.example.Test@method:10:code |==> 
2:CONDITIONALS_BOUNDARY:org.example.Test@method:15:x > 0 |==> x >= 0
"""
        log_file = temp_dir / "mutants.log"
        log_file.write_text(log_content)
        
        mutations = mutation_parser.parse_all_mutations(log_file)
        
        # Should filter out duplicates (same line, same mutator)
        assert len(mutations) == 2