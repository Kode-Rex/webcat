#!/usr/bin/env python
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Script to run all tests for the WebCat project.
This script ensures the proper import paths are set up before running tests.
"""
import os
import sys

import pytest

# Update path to import from current directory structure
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
