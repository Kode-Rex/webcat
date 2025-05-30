#!/bin/bash
set -e

# Navigate to the tests directory
cd "$(dirname "$0")"

echo "Running MCP server tests..."

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install test dependencies
pip install pytest fastapi requests-mock httpx pytest-cov
pip install python-dotenv requests beautifulsoup4 readability-lxml

# Copy the MCP server to the tests directory for accurate coverage reporting
cp ../mcp_server.py .

# Run the tests with coverage report
pytest test_mcp_server.py -v --cov=mcp_server --cov-report=term

# Clean up the copied file
rm -f mcp_server.py

# Deactivate the virtual environment
deactivate

echo "Tests completed successfully!" 