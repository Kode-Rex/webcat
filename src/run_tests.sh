#!/bin/bash
# Script to run all WebCat tests
# This script activates the virtual environment and runs the tests

# Move to the src directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
else
  echo "Error: Virtual environment not found in src/.venv"
  echo "Please create a virtual environment and install dependencies first."
  exit 1
fi

# Get the absolute path to the src directory
SRC_PATH=$(pwd)

# Run the tests with proper Python path
echo "Running WebCat tests..."
cd ..
PYTHONPATH="$SRC_PATH:$PYTHONPATH" python -m pytest -v tests/

# Return the exit code from the test command
exit $? 