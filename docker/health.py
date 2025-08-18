"""Health endpoints module for WebCat MCP server."""

import os
import time
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

logger = logging.getLogger(__name__)

def setup_health_endpoints(app: FastAPI):
    """Setup health and utility endpoints for the WebCat server."""
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        try:
            return {
                "status": "healthy",
                "service": "webcat-mcp",
                "timestamp": time.time(),
                "version": "2.2.0",
                "uptime": "running"
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": time.time()
                }
            )
    
    @app.get("/client")
    async def sse_client():
        """Serve the WebCat SSE demo client."""
        try:
            current_dir = Path(__file__).parent
            client_path = current_dir.parent / "examples" / "webcat_client.html"
            
            logger.info(f"Looking for client file at: {client_path}")
            
            if client_path.exists():
                html_content = client_path.read_text(encoding="utf-8")
                logger.info("Successfully loaded WebCat demo client")
                return HTMLResponse(content=html_content)
            else:
                logger.error(f"WebCat client file not found at: {client_path}")
                return JSONResponse(
                    status_code=404,
                    content={
                        "error": "WebCat client file not found",
                        "expected_path": str(client_path),
                        "exists": False
                    }
                )
        except Exception as e:
            logger.error(f"Failed to serve WebCat client: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to serve WebCat client", 
                    "details": str(e)
                }
            )
    
    @app.get("/status")
    async def server_status():
        """Detailed server status endpoint."""
        try:
            return {
                "service": "WebCat MCP Server",
                "status": "running",
                "version": "2.2.0",
                "timestamp": time.time(),
                "configuration": {
                    "serper_api_configured": bool(os.environ.get("SERPER_API_KEY")),
                    "port": int(os.environ.get("PORT", 8000)),
                    "log_level": os.environ.get("LOG_LEVEL", "INFO"),
                    "log_dir": os.environ.get("LOG_DIR", "/tmp")
                },
                "endpoints": {
                    "main_mcp": "/mcp",
                    "sse_demo": "/sse", 
                    "health": "/health",
                    "status": "/status",
                    "demo_client": "/client"
                },
                "capabilities": [
                    "Web search with Serper API",
                    "DuckDuckGo fallback search",
                    "Content extraction and scraping",
                    "Markdown conversion",
                    "FastMCP protocol support",
                    "SSE streaming",
                    "Demo UI client"
                ]
            }
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Failed to get server status",
                    "details": str(e),
                    "timestamp": time.time()
                }
            )
    
    @app.get("/")
    async def root():
        """Root endpoint with basic information."""
        return {
            "service": "WebCat MCP Server",
            "version": "2.2.0",
            "description": "Web search and content extraction with MCP protocol support",
            "endpoints": {
                "demo_client": "/client",
                "health": "/health",
                "status": "/status",
                "mcp_sse": "/mcp"
            },
            "documentation": "Access /client for the demo interface"
        }

def create_health_app() -> FastAPI:
    """Create a separate FastAPI app for health endpoints."""
    app = FastAPI(
        title="WebCat MCP Health Service",
        description="Health monitoring and demo client for WebCat MCP server",
        version="2.2.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    setup_health_endpoints(app)
    return app

def create_demo_app() -> FastAPI:
    """Create the main demo app with both health and SSE endpoints."""
    app = FastAPI(
        title="WebCat MCP Demo Server",
        description="Complete WebCat MCP server with demo UI and SSE streaming",
        version="2.2.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    setup_health_endpoints(app)
    return app
