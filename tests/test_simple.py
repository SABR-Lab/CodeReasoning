#!/usr/bin/env python3
"""
Simple test that actually works with your code
"""

import sys
from pathlib import Path
import tempfile

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_imports():
    """Test that we can import your modules"""
    print("Testing basic imports...")
    
    try:
        from core.mutation_parser import MutationParser
        from core.mutation_applier import MutationApplier
        from core.coverage_runner import CoverageRunner
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_parser_simple():
    """Test the parser with a simple line"""
    print("\nTesting parser with simple line...")
    
    from core.mutation_parser import MutationParser
    parser = MutationParser()
    
    # Test line from YOUR original code format
    test_line = "1:VOID_METHOD_CALLS:org.example.Test.voidMethod()V:org.example.Test.voidMethod()V:org.example.Test@testMethod:10:someObject.voidMethod() |==> "
    
    # Try different method names based on your actual code
    if hasattr(parser, 'parse_mutant_line'):
        result = parser.parse_mutant_line(test_line)
        method_name = 'parse_mutant_line'
    elif hasattr(parser, 'parse_mutant_line'):
        result = parser.parse_mutant_line(test_line)
        method_name = 'parse_mutant_line'
    elif hasattr(parser, 'parse_mutants_log'):
        result = parser.parse_mutants_log(test_line)
        method_name = 'parse_mutants_log'
    else:
        print("❌ No known parsing method found")
        return False
    
    print(f"Using method: {method_name}")
    
    if result:
        print(f"✅ Parser returned result: {result.get('mutant_id', 'N/A')}")
        return True
    else:
        print("❌ Parser returned None")
        return False

def main():
    """Run simple tests"""
    print("Running Simple Tests for Your Code")
    print("=" * 50)
    
    tests = [
        test_basic_imports(),
        test_parser_simple(),
    ]
    
    print("\n" + "=" * 50)
    passed = sum(tests)
    total = len(tests)
    
    if passed == total:
        print(f"✅ All {passed}/{total} tests passed!")
        return 0
    else:
        print(f"❌ {total - passed}/{total} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())