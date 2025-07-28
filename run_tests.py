#!/usr/bin/env python3
"""
Main test runner for the credit portfolio analyzer.
"""

import sys
import subprocess
import os


def run_part_a_tests():
    """Run Part A tests."""
    print("=" * 60)
    print("RUNNING PART A TESTS")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "test/test_part_a.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Part A tests completed successfully")
            return True
        else:
            print("❌ Part A tests failed")
            return False
    except Exception as e:
        print(f"❌ Error running Part A tests: {e}")
        return False


def run_part_b_tests():
    """Run Part B tests."""
    print("=" * 60)
    print("RUNNING PART B TESTS")
    print("=" * 60)
    
    try:
        result = subprocess.run([
            sys.executable, "test/test_part_b.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Part B tests completed successfully")
            return True
        else:
            print("❌ Part B tests failed")
            return False
    except Exception as e:
        print(f"❌ Error running Part B tests: {e}")
        return False


def main():
    """Run all test suites."""
    print("=" * 60)
    print("CREDIT PORTFOLIO ANALYSIS - TEST SUITE")
    print("=" * 60)
    
    # Run Part A tests
    part_a_success = run_part_a_tests()
    
    # Run Part B tests
    part_b_success = run_part_b_tests()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if part_a_success and part_b_success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 