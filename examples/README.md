# WebCat Demo UI

This directory contains the WebCat demo UI and related components for testing and demonstrating the WebCat MCP server functionality.

## 🎨 Demo Client

The `webcat_client.html` file provides a complete web-based demo interface for the WebCat MCP server featuring:

- **Real-time SSE connection** to the WebCat server
- **Interactive search interface** with customizable parameters
- **Live result display** with formatted search results
- **Health monitoring** and server status checks
- **Beautiful, responsive UI** with modern styling
- **Auto-connection** for development convenience

## 🚀 Quick Start

### Option 1: Use Docker (Recommended)

```bash
# Run the demo server with UI
docker run -p 8000:8000 -p 8001:8001 \
  -e WEBCAT_MODE=demo \
  -e SERPER_API_KEY=your_key \
  tmfrisinger/webcat:latest

# Or build locally
cd docker
./build.sh
docker run -p 8000:8000 -p 8001:8001 webcat:latest
```

### Option 2: Local Development

```bash
cd docker
python cli.py --mode demo --port 8000
```

## 📡 Endpoints

When running in demo mode, you'll have access to:

- **🎨 Demo UI**: http://localhost:8001/client
- **💗 Health Check**: http://localhost:8001/health
- **📊 Server Status**: http://localhost:8001/status
- **🔗 SSE Stream**: http://localhost:8000/sse
- **🛠️ FastMCP**: http://localhost:8000/mcp

## 🎯 Features

### Search Functionality
- Enter any search query
- Choose number of results (3, 5, or 10)
- Real-time streaming of search progress
- Formatted display of results with content extraction

### Server Integration
- Auto-connects to localhost for development
- Supports both Serper API and DuckDuckGo fallback
- Real-time status updates via Server-Sent Events
- Comprehensive error handling and logging

### UI Features
- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Logs**: Live debugging and status information
- **Connection Management**: Easy connect/disconnect controls
- **Result Display**: Formatted search results with content previews

## 🔧 Configuration

### Environment Variables

- `SERPER_API_KEY`: Your Serper API key (optional - falls back to DuckDuckGo)
- `PORT`: Main server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `WEBCAT_MODE`: Server mode - use "demo" for UI support

### URL Parameters

The SSE endpoint supports these parameters:

- `operation`: Operation type (`connect`, `search`, `health`)
- `query`: Search query for search operations
- `max_results`: Maximum number of results (default: 5)

Example:
```
http://localhost:8000/sse?operation=search&query=python&max_results=3
```

## 🛠️ Development

### File Structure

```
examples/
├── webcat_client.html    # Main demo client
└── README.md            # This file

docker/
├── cli.py              # CLI entry point
├── demo_server.py      # Demo server with SSE
├── health.py           # Health endpoints
├── api_tools.py        # FastMCP tools
└── mcp_server.py       # Original MCP server
```

### Customization

The demo client can be customized by:

1. **Modifying the HTML/CSS/JS** in `webcat_client.html`
2. **Adding new tools** in `api_tools.py`
3. **Extending SSE operations** in `demo_server.py`
4. **Adding health endpoints** in `health.py`

### Testing

```bash
# Test the demo server
cd docker
python cli.py --mode demo --port 8000

# Test individual components
python -m pytest tests/
```

## 📝 SSE Message Types

The SSE stream uses these message types:

```json
{"type": "connection", "status": "connected", "message": "Stream started"}
{"type": "status", "message": "Processing request..."}
{"type": "data", "data": {...}, "title": "Optional title"}
{"type": "complete", "message": "Operation finished"}
{"type": "error", "message": "Error description"}
{"type": "heartbeat", "timestamp": 1234567890}
```

## 🔍 Troubleshooting

### Common Issues

1. **Connection Failed**: Check that the server is running on the expected port
2. **No Search Results**: Verify your search query and API configuration
3. **CORS Errors**: Ensure the server has CORS middleware enabled
4. **SSE Connection Drops**: Check network connectivity and server logs

### Debug Tips

- Use the browser's Developer Tools to inspect SSE messages
- Check the real-time logs in the demo UI
- Verify health endpoints are accessible
- Test with different search queries and parameters

## 🎉 Success Indicators

A successful setup will show:

- ✅ Auto-connection to localhost
- ✅ "Connected to FastMCP server" status
- ✅ Real-time search results with content
- ✅ Health check passes
- ✅ Server status shows "healthy"

## 📚 Further Reading

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Server-Sent Events (SSE) Guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [WebCat Project README](../README.md)
