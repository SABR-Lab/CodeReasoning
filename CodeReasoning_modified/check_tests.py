#!/usr/bin/env python3
"""
Check which tests are being discovered
"""

import os
import sys

def check_test_discovery():
    """Check which test files are being discovered"""
    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    print("Checking test files in:", tests_dir)
    print("=" * 50)
    
    if not os.path.exists(tests_dir):
        print("ERROR: tests directory not found!")
        return
    
    # List all test files
    test_files = []
    for file in os.listdir(tests_dir):
        if file.startswith('test_') and file.endswith('.py'):
            test_files.append(file)
    
    print(f"Found {len(test_files)} test files:")
    for file in sorted(test_files):
        file_path = os.path.join(tests_dir, file)
        print(f"  ✓ {file} (exists: {os.path.exists(file_path)})")
    
    print("\n" + "=" * 50)
    print("Test files that should be found:")
    expected_files = [
        'test_mutation_parser.py',
        'test_mutation_applier.py', 
        'test_coverage_runner.py',
        'test_validation.py',
        'test_integration.py',
        'conftest.py'
    ]
    
    for expected in expected_files:
        exists = expected in test_files
        status = "✓" if exists else "✗"
        print(f"  {status} {expected}")

if __name__ == "__main__":
    check_test_discovery()