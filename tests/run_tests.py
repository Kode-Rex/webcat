#!/usr/bin/env python
"""
Helper script to run tests for the WebCat Azure Functions.
"""
import os
import sys
import pytest

# Add the parent directory to the path so tests can import the function_app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # Run pytest with verbose output
    exit_code = pytest.main(["-v", os.path.dirname(os.path.abspath(__file__))])
    sys.exit(exit_code) 