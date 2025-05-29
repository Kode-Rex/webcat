#!/usr/bin/env python
"""
Script to run all tests for the WebCat project.
This script ensures the proper import paths are set up before running tests.
"""
import os
import sys
import pytest

# Add the src directory to the path so tests can import function_app
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

def main():
    """Run all tests in the tests directory."""
    print("Running WebCat tests...")
    # Run pytest with verbose output
    exit_code = pytest.main(["-v", os.path.dirname(os.path.abspath(__file__))])
    
    if exit_code == 0:
        print("All tests passed successfully!")
    else:
        print(f"Tests completed with exit code: {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main()) 