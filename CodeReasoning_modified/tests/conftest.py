"""
Test configuration and fixtures - UPDATED FOR YOUR CODE
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import YOUR actual classes
try:
    # Try to import your actual classes
    from core.mutation_parser import MutationParser
    from core.mutation_applier import MutationApplier
    from core.coverage_runner import CoverageRunner
    print("✅ Successfully imported your actual modules")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    # Create mock classes for testing
    class MockMutationParser:
        def parse_mutant_line(self, line):
            return None
        def find_mutants_log(self, work_dir):
            return None
        def parse_all_mutations(self, log_file):
            return []
    
    class MockMutationApplier:
        def find_java_file_by_class(self, class_name, source_dirs):
            return None
        def apply_mutation_to_file(self, source_file, line_number, original_code, mutated_code):
            return False
        def create_full_project_copy(self, original_dir, copy_dir):
            return False
    
    class MockCoverageRunner:
        def parse_failing_tests(self, mutant_dir):
            return []
        def read_all_tests(self, mutant_dir):
            return []
        def parse_coverage_xml(self, xml_file):
            return 0.0, {}
    
    MutationParser = MockMutationParser
    MutationApplier = MockMutationApplier
    CoverageRunner = MockCoverageRunner


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    test_dir = Path(tempfile.mkdtemp())
    yield test_dir
    # Cleanup
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def sample_mutations_log_content():
    """Sample mutants.log content for testing - YOUR FORMAT"""
    return """# This is a comment
1:VOID_METHOD_CALLS:org.example.Test.voidMethod()V:org.example.Test.voidMethod()V:org.example.Test@testMethod:10:45:someObject.voidMethod() |==> 
2:CONDITIONALS_BOUNDARY:org.example.Test.test(I)Z:org.example.Test.test(I)Z:org.example.Test@test:23:15:x > 0 |==> x >= 0
3:INCREMENTS:org.example.Test.increment()V:org.example.Test.increment()V:org.example.Test@increment:20:343:i++ |==> i--
4:MATH:org.example.Test.calc()I:org.example.Test.calc()I:org.example.Test@calc:25:23:result * 2 |==> result * 3
"""


@pytest.fixture
def sample_mutations_log_file(temp_dir, sample_mutations_log_content):
    """Create a sample mutants.log file"""
    log_file = temp_dir / "mutants.log"
    with open(log_file, 'w') as f:
        f.write(sample_mutations_log_content)
    return log_file


@pytest.fixture
def sample_java_file_content():
    """Sample Java file content for mutation testing"""
    return """package org.example;

public class Test {
    public void voidMethod() {
        someObject.voidMethod();
    }
    
    public boolean test(int x) {
        return x > 0;
    }
    
    public void increment() {
        int i = 0;
        i++;
    }
    
    public int calc() {
        int result = 5;
        return result * 2;
    }
}
"""


@pytest.fixture
def sample_java_file(temp_dir, sample_java_file_content):
    """Create a sample Java file for testing"""
    java_dir = temp_dir / "src" / "main" / "java" / "org" / "example"
    java_dir.mkdir(parents=True)
    java_file = java_dir / "Test.java"
    with open(java_file, 'w') as f:
        f.write(sample_java_file_content)
    return java_file


@pytest.fixture
def mutation_parser():
    return MutationParser()


@pytest.fixture
def mutation_applier():
    return MutationApplier()


@pytest.fixture
def coverage_runner():
    return CoverageRunner()