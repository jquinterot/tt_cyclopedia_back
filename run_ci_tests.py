#!/usr/bin/env python3
"""
CI test runner optimized for Docker environment.
Runs a subset of tests for faster CI feedback.
"""
import subprocess
import sys
import os

def run_tests():
    """Run a subset of tests for faster CI feedback."""
    # Run only TestSetup classes for faster execution
    test_patterns = [
        "app/tests/test_users.py::TestSetup",
        "app/tests/test_posts.py::TestSetup", 
        "app/tests/test_forums.py::TestSetup",
        "app/tests/test_comments.py::TestSetup"
    ]
    
    cmd = [
        "python3", "-m", "pytest",
        "--maxfail=10",
        "--disable-warnings",
        "-q",
        "--tb=short"
    ] + test_patterns
    
    print("Running CI tests (subset for speed)...")
    print(f"Command: {' '.join(cmd)}")
    
    # Set environment for better performance
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    # Don't capture output to see real-time progress
    result = subprocess.run(cmd, env=env)
    
    print(f"Exit code: {result.returncode}")
    
    if result.returncode == 0:
        print("✅ CI tests passed!")
    else:
        print("❌ CI tests failed!")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 