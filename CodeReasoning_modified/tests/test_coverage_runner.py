"""
Tests for coverage runner functionality
"""

import pytest
from pathlib import Path
import tempfile


class TestCoverageRunner:
    """Test CoverageRunner class"""
    
    def test_parse_failing_tests(self, coverage_runner, temp_dir):
        """Test parsing failing tests file"""
        failing_tests_content = """--- org.example.Test.test1
--- org.example.Test.test2
some other content
--- org.example.Test.test3
"""
        failing_file = temp_dir / "failing_tests"
        failing_file.write_text(failing_tests_content)
        
        failed_tests = coverage_runner.parse_failing_tests(temp_dir)
        
        assert len(failed_tests) == 3
        assert "org.example.Test.test1" in failed_tests
        assert "org.example.Test.test2" in failed_tests
        assert "org.example.Test.test3" in failed_tests
    
    def test_parse_failing_tests_file_not_found(self, coverage_runner, temp_dir):
        """Test when failing_tests file doesn't exist"""
        failed_tests = coverage_runner.parse_failing_tests(temp_dir)
        
        assert failed_tests == []
    
    def test_read_all_tests(self, coverage_runner, temp_dir):
        """Test reading all tests file"""
        all_tests_content = """org.example.Test.test1
org.example.Test.test2
org.example.Test.test3
"""
        all_tests_file = temp_dir / "all_tests"
        all_tests_file.write_text(all_tests_content)
        
        all_tests = coverage_runner.read_all_tests(temp_dir)
        
        assert len(all_tests) == 3
        assert "org.example.Test.test1" in all_tests
        assert "org.example.Test.test2" in all_tests
        assert "org.example.Test.test3" in all_tests
    
    def test_read_all_tests_file_not_found(self, coverage_runner, temp_dir):
        """Test when all_tests file doesn't exist"""
        all_tests = coverage_runner.read_all_tests(temp_dir)
        
        assert all_tests == []
    
    def test_parse_coverage_xml_valid(self, coverage_runner, temp_dir):
        """Test parsing valid coverage XML"""
        coverage_xml_content = """<?xml version="1.0" ?>
<coverage line-rate="0.75" branch-rate="0.0">
    <class name="org.example.Test">
        <method name="testMethod" signature="()V">
            <line number="10" hits="1"/>
            <line number="11" hits="1"/>
            <line number="12" hits="0"/>
        </method>
        <method name="anotherMethod" signature="(I)Z">
            <line number="15" hits="1"/>
        </method>
    </class>
</coverage>
"""
        xml_file = temp_dir / "coverage.xml"
        xml_file.write_text(coverage_xml_content)
        
        coverage_percentage, branch_coverage, method_data = coverage_runner.parse_coverage_xml(xml_file)
        
        # Line-rate from XML
        assert coverage_percentage == 0.75
        assert "org.example.Test.testMethod()V" in method_data
        assert "org.example.Test.anotherMethod(I)Z" in method_data
        assert branch_coverage == 0.0
        assert method_data["org.example.Test.testMethod()V"] == ['10|1', '11|1']
    
    def test_parse_coverage_xml_file_not_found(self, coverage_runner, temp_dir):
        """Test when coverage XML file doesn't exist"""
        coverage_percentage, branch_coverage, method_data = coverage_runner.parse_coverage_xml(temp_dir / "nonexistent.xml")
        
        assert coverage_percentage == 0.0
        assert branch_coverage == 0.0
        assert method_data == {}
    
    def test_parse_coverage_xml_invalid(self, coverage_runner, temp_dir):
        """Test parsing invalid coverage XML"""
        invalid_xml = "not valid xml content"
        xml_file = temp_dir / "coverage.xml"
        xml_file.write_text(invalid_xml)
        
        coverage_percentage, branch_coverage, method_data = coverage_runner.parse_coverage_xml(xml_file)
        
        assert coverage_percentage == 0.0
        assert branch_coverage == 0.0
        assert method_data == {}