#!/usr/bin/env python3
"""
Test runner script for the FastAPI application.
This script runs all unit tests with proper configuration.
"""

import sys
import os
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests using pytest"""
    
    # Add the app directory to Python path
    app_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(app_dir))
    
    # Test directory
    test_dir = Path(__file__).parent
    
    # Run pytest with verbose output and coverage
    cmd = [
        "python", "-m", "pytest",
        str(test_dir),
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--cov=app",  # Coverage for app module
        "--cov-report=term-missing",  # Show missing lines in coverage
        "--cov-report=html:htmlcov",  # Generate HTML coverage report
        "--cov-report=xml",  # Generate XML coverage report
        "-W", "ignore::DeprecationWarning",  # Ignore deprecation warnings
        "-W", "ignore::PendingDeprecationWarning"  # Ignore pending deprecation warnings
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All tests passed successfully!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Please install pytest: pip install pytest pytest-cov")
        return 1

def run_specific_test(test_file):
    """Run a specific test file"""
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        print(f"❌ Test file {test_file} not found")
        return 1
    
    cmd = [
        "python", "-m", "pytest",
        str(test_path),
        "-v",
        "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Test {test_file} passed successfully!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test {test_file} failed with exit code {e.returncode}")
        return e.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code) 