# WebCat MCP Server

This directory contains the **FastMCP-based Model Context Protocol (MCP) server** that provides web search capabilities for AI models.

## Features

- 🔍 **Web search with content extraction** - Full webpage scraping and markdown conversion
- 🆓 **Free DuckDuckGo fallback** - Works without any API keys required
- ⚡ **Serper API integration** - Premium search results when API key is provided
- 🐳 **Containerized deployment** - Easy Docker-based setup
- 🧪 **MCP-compliant protocol** - Compatible with MCP clients like Claude Desktop
- 📊 **Comprehensive logging** - Detailed logs with rotation
- ✅ **Full test coverage** - Pytest-based test suite

## Prerequisites

- Docker
- Python 3.11+ (for local development)
- Serper API key (optional - falls back to DuckDuckGo search if not provided)

## Quick Start

### 1. Build and Run with Docker

```bash
# Build the image
./build.sh

# Generate a secure API key (choose one method)
export WEBCAT_API_KEY="sk-webcat-$(openssl rand -hex 32)"
# OR use your own secure string
export WEBCAT_API_KEY="sk-webcat-my-secure-key-2024"

# Run with free DuckDuckGo fallback (no external API key needed)
docker run -p 8000:8000 \
  -e WEBCAT_API_KEY="$WEBCAT_API_KEY" \
  webcat:latest

# Or run with premium Serper API
docker run -p 8000:8000 \
  -e WEBCAT_API_KEY="$WEBCAT_API_KEY" \
  -e SERPER_API_KEY=your_serper_api_key \
  webcat:latest
```

### 2. Using Docker Compose

```bash
# Generate your secure API key
export WEBCAT_API_KEY="sk-webcat-$(openssl rand -hex 32)"

# Optionally set Serper API key for premium search
export SERPER_API_KEY=your_serper_api_key  # Optional

# Start the server
docker-compose up
```

## Configuration

### Environment Variables

- `WEBCAT_API_KEY`: **Required** - Your custom API key for authentication (user-generated security token)
- `SERPER_API_KEY`: **Optional** - Serper API key for premium search (falls back to DuckDuckGo if not set)
- `PORT`: Port to run the server on (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_DIR`: Directory for log files (default: /tmp)

### API Key Security

The `WEBCAT_API_KEY` is a **user-generated security token** that you create to protect your WebCat server:

- 🔐 **You generate it** - Create any secure string (e.g., `sk-webcat-your-secret-key-123`)
- 🛡️ **Authentication layer** - Prevents unauthorized access to your search server
- 🔑 **Required for all requests** - MCP clients must provide this key to use the server
- 💡 **Best practices**: Use a long, random string with prefixes like `sk-webcat-` for clarity

Example secure keys:
```bash
export WEBCAT_API_KEY="sk-webcat-$(openssl rand -hex 32)"
export WEBCAT_API_KEY="webcat-prod-$(date +%s)-$(openssl rand -hex 16)"
export WEBCAT_API_KEY="sk-webcat-my-secure-key-2024"
```

## MCP Protocol Endpoints

The server runs on **FastMCP** and exposes MCP protocol endpoints:

- **Base URL**: `http://localhost:8000/mcp/`
- **Protocol**: JSON-RPC 2.0 over HTTP
- **Transport**: Streamable HTTP

### Available Tools

1. **`search`** - Search the web for information
   - Uses Serper API if key is available
   - Falls back to DuckDuckGo automatically
   - Returns full webpage content in markdown format

2. **`health_check`** - Check server health status

## Testing the Server

### Method 1: Quick Health Check

```bash
# Simple connectivity test (may show session errors but confirms server is running)
curl -v http://localhost:8000/mcp/

# Check if container is running and responsive
docker logs <container_id> --tail 5
```

### Method 2: Run Tests (Recommended)

#### Core Functionality Tests
```bash
# Run DuckDuckGo fallback tests
python -m pytest test_duckduckgo_fallback.py -v

# Run specific test
python -m pytest test_duckduckgo_fallback.py::test_duckduckgo_fallback -v -s

# Run with coverage
python -m pytest test_duckduckgo_fallback.py --cov=mcp_server -v
```

#### API Integration Tests
```bash
# Test Serper API directly (requires SERPER_API_KEY)
python test_serper.py

# Test DuckDuckGo API directly (no API key needed)
python -c "from mcp_server import fetch_duckduckgo_search_results; print(fetch_duckduckgo_search_results('test query', 1))"
```

#### MCP Protocol Tests
```bash
# Test complete MCP protocol flow
python test_mcp_protocol.py

# Just check if server is running
python test_mcp_protocol.py --check-health
```

### Method 3: Test MCP Protocol Directly

**⚠️ Note**: `streamable-http` requires proper MCP initialization flow. Here's the correct sequence:

#### Step 1: Initialize MCP Session
```bash
# Initialize the MCP session
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }'
```

#### Step 2: Extract Session ID
Look for `Mcp-Session-Id` header in the response, then use it for subsequent requests:

```bash
# Use the session ID from step 1 (replace YOUR_SESSION_ID)
curl -X POST http://localhost:8000/mcp/ \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }'
```

**For reliable testing, use the pytest suite instead** - it properly handles the MCP protocol complexities.

### Method 4: Test with MCP Client

Use with Claude Desktop or other MCP-compatible clients:

```json
{
  "mcpServers": {
    "webcat": {
      "command": "docker",
      "args": ["run", "-i", "--rm", 
               "-e", "WEBCAT_API_KEY=your_key",
               "webcat:latest"]
    }
  }
}
```

## Search Functionality

### DuckDuckGo Fallback (Free)

When no `SERPER_API_KEY` is configured:
- ✅ **Completely free** - No API keys required
- ✅ **No rate limits** - Uses DuckDuckGo's public search
- ✅ **Full content scraping** - Extracts and converts to markdown
- ✅ **Automatic fallback** - Seamless when Serper fails

### Serper API (Premium)

When `SERPER_API_KEY` is configured:
- 🚀 **Higher quality results** - Google-powered search
- 📊 **Better ranking** - More relevant results
- ⚡ **Faster responses** - Optimized API
- 💰 **Paid service** - Requires Serper API subscription

## Test Results Example

```bash
$ python -m pytest test_duckduckgo_fallback.py -v

=========================================== test session starts ============================================
collected 3 items                                                                                          

test_duckduckgo_fallback.py::test_duckduckgo_fallback PASSED                                         [ 33%]
test_duckduckgo_fallback.py::test_duckduckgo_search_structure PASSED                                 [ 66%]
test_duckduckgo_fallback.py::test_duckduckgo_error_handling PASSED                                   [100%]

============================================ 3 passed in 3.08s ============================================
```

## Logs and Debugging

### View Docker Logs

```bash
# Get container ID
docker ps

# View logs
docker logs <container_id>

# Follow logs in real-time
docker logs -f <container_id>
```

### Log Files

- **Location**: `/var/log/webcat/webcat.log` (inside container)
- **Rotation**: 10MB per file, 5 backup files
- **Format**: Timestamp, level, message with full context

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server locally
python mcp_server.py
```

### Running Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
python -m pytest test_duckduckgo_fallback.py -v

# Run with coverage
python -m pytest test_duckduckgo_fallback.py --cov=mcp_server --cov-report=html
```

## Troubleshooting

### Common Issues

1. **"Not Found" responses**
   - Make sure you're using the correct endpoint: `/mcp/`
   - Include proper headers: `Accept: application/json, text/event-stream`

2. **"Missing session ID" errors**
   - Use pytest tests for validation instead of direct curl
   - MCP protocol requires session management

3. **No search results**
   - Check if DuckDuckGo is accessible from your network
   - Verify SERPER_API_KEY if using premium search
   - Check Docker logs for detailed error messages

4. **Import errors in tests**
   - Ensure you're in the `docker/` directory when running tests
   - Verify virtual environment is activated
   - Check that all dependencies are installed

### Getting Help

- Check Docker logs: `docker logs <container_id>`
- Run health check: Use pytest to verify functionality
- Review test output for detailed error information

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   FastMCP Server │───▶│  Search APIs    │
│ (Claude Desktop)│    │   (Port 8000)    │    │ Serper/DuckDDG  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Content Scraper │
                       │   (Readability)  │
                       └──────────────────┘
```

The server acts as an MCP-compliant bridge between AI models and web search capabilities, with automatic fallback to free services when premium APIs are unavailable. 