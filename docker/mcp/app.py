"""FastAPI application for the MCP server."""

import logging
import os
import time
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from .models import QueryRequest, SearchResponse, SearchResult, ErrorResponse
from .services import fetch_search_results, process_search_results

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory API key
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

# Function to set the API key (for testing)
def set_api_key(key: str) -> None:
    """Set the API key (for testing)."""
    global SERPER_API_KEY
    SERPER_API_KEY = key

# Initialize FastAPI app
app = FastAPI(
    title="Model Context Protocol (MCP) Server",
    description="A server for providing search context to models following the MCP protocol",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory rate limiting
rate_limit_store = {}
RATE_LIMIT = 10  # requests
RATE_LIMIT_WINDOW = 60  # seconds

# Custom exception handler for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status_code=exc.status_code,
            message=exc.detail,
            error_type="http_exception"
        ).dict()
    )

# Rate limiting dependency
async def check_rate_limit(request: Request):
    """Check rate limiting for requests."""
    client_ip = request.client.host
    current_time = time.time()
    
    # Initialize or clean up rate limit data
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Remove old timestamps
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store[client_ip]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Add current request timestamp
    rate_limit_store[client_ip].append(current_time)
    
    # Add rate limit headers to response
    remaining = RATE_LIMIT - len(rate_limit_store[client_ip])
    
    # Return headers to be added to the response
    return {
        "X-Rate-Limit-Limit": str(RATE_LIMIT),
        "X-Rate-Limit-Remaining": str(remaining),
        "X-Rate-Limit-Reset": str(int(current_time + RATE_LIMIT_WINDOW))
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "webcat"}

@app.post("/api/v1/search", response_model=SearchResponse, tags=["Search API"])
async def search(
    request: QueryRequest, 
    response: Response,
    rate_limit_headers: Dict[str, str] = Depends(check_rate_limit)
):
    """
    Search the web and return results with content.
    
    This endpoint follows the Model Context Protocol (MCP) for providing
    search results that can be used as context for AI models.
    
    - **query**: The search query to execute
    - **api_key**: Optional API key to override the server's key
    
    Returns a SearchResponse object containing search results with content.
    """
    try:
        global SERPER_API_KEY
        query = request.query
        
        # Add rate limit headers to response
        for header_name, header_value in rate_limit_headers.items():
            response.headers[header_name] = header_value
            
        # Use the in-memory API key, or allow overriding with a request parameter
        api_key = request.api_key or SERPER_API_KEY
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Serper API key not configured. Please provide an api_key in the request."
            )
            
        logging.info(f'MCP search: [{query}]')
        
        # Fetch search results
        results = fetch_search_results(query, api_key)
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="No search results found"
            )
        
        # Process search results
        processed_results = process_search_results(results)
        
        # Return response
        return SearchResponse(
            query=query,
            result_count=len(processed_results),
            results=processed_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error: {str(e)}"
        )

# Legacy endpoint for backward compatibility
@app.post("/api/search", response_model=SearchResponse, tags=["Legacy"])
async def search_legacy(
    request: QueryRequest, 
    response: Response,
    rate_limit_headers: Dict[str, str] = Depends(check_rate_limit)
):
    """Legacy search endpoint. Use /api/v1/search instead."""
    return await search(request, response, rate_limit_headers)

# Customize OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Model Context Protocol API",
        version="1.0.0",
        description="API for Model Context Protocol (MCP) providing search context for AI models",
        routes=app.routes,
    )
    
    # Add additional metadata
    openapi_schema["info"]["contact"] = {
        "name": "WebCAT MCP",
        "url": "https://github.com/yourusername/webcat",
        "email": "your-email@example.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("mcp.app:app", host="0.0.0.0", port=port, reload=False) 