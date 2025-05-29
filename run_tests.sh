#!/bin/bash
# Script to run all WebCat tests
# This script activates the virtual environment and runs the tests

# Move to the project root directory
cd "$(dirname "$0")"

# Check if virtual environment exists in src
if [ -d "../src/.venv" ]; then
  echo "Activating virtual environment..."
  source ../src/.venv/bin/activate
else
  echo "Error: Virtual environment not found in src/.venv"
  echo "Please create a virtual environment and install dependencies first."
  exit 1
fi

# Run the tests
echo "Running WebCat tests..."
python run_all_tests.py

# Return the exit code from the test script
exit $? 