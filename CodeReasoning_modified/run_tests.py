#!/usr/bin/env python3
"""
Test runner for Defects4J Mutant Generator
"""

import pytest
import sys
import os

def main():
    """Run all tests"""
    print("Running Defects4J Mutant Generator Tests")
    print("=" * 50)
    
    # Add the tests directory to Python path
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    
    # Run pytest with specific configuration
    result = pytest.main([
        "tests/",  # Run all tests in tests directory
        "-v",  # verbose
        "--tb=short",  # shorter tracebacks
        # Remove -x to see all failures, not just first one
        "--disable-warnings",  # cleaner output
        "--collect-only",  # First show what tests are discovered
    ])
    
    # If collection worked, run actual tests
    if result == 0:
        print("\n" + "=" * 50)
        print("Running actual tests...")
        result = pytest.main([
            "tests/",
            "-v",
            "--tb=short", 
            "--disable-warnings",
        ])
    
    sys.exit(result)

if __name__ == "__main__":
    main()