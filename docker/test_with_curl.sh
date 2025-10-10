#!/bin/bash
# Simple curl-based test for WebCat endpoints

echo "=== Testing WebCat Server ==="
echo ""

# Test health endpoint
echo "1. Health Check (no auth):"
curl -s http://localhost:8000/health | jq .
echo ""

# Test status endpoint
echo "2. Status Check:"
curl -s http://localhost:8000/status | jq .
echo ""

# Test with auth if WEBCAT_API_KEY is set
if [ -n "$WEBCAT_API_KEY" ]; then
    echo "3. Health Check (with auth):"
    curl -s -H "Authorization: Bearer $WEBCAT_API_KEY" http://localhost:8000/health | jq .
    echo ""
fi

echo "=== MCP Tools Testing ==="
echo "MCP tools (search, health_check) require an MCP client."
echo "Use Claude Desktop or run: python test_mcp_client.py"
