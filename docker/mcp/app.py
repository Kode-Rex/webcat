"""FastAPI application for the MCP server."""

import logging
import logging.handlers
import os
import time
import asyncio
from typing import Dict, List, Optional, Any, AsyncIterator
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi
from sse_starlette.sse import EventSourceResponse

from .models import QueryRequest, SearchResponse, SearchResult, ErrorResponse
from .services import fetch_search_results, process_search_results

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.environ.get("LOG_DIR", "/var/log/webcat")
LOG_FILE = os.path.join(LOG_DIR, "webcat.log")

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create formatters
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setup console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Setup rotating file handler (10MB per file, keep 5 backup files)
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logging.info("Logging initialized with file rotation at %s", LOG_FILE)

# In-memory API key
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
WEBCAT_API_KEY = os.environ.get("WEBCAT_API_KEY", "")

# Improved logging for API keys
if WEBCAT_API_KEY:
    key_length = len(WEBCAT_API_KEY)
    masked_key = WEBCAT_API_KEY[:4] + "*" * (key_length - 8) + WEBCAT_API_KEY[-4:] if key_length > 8 else "****"
    logging.info(f"WEBCAT_API_KEY is set (masked: {masked_key})")
else:
    logging.warning("WEBCAT_API_KEY is not set! The 'webcat' API key path will not work.")

logging.info(f"Using API key from environment: {'Set' if SERPER_API_KEY else 'Not set'}")

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

# Server-Sent Events search endpoint
@app.post("/search/{api_key}/sse")
async def search_with_key_sse(
    api_key: str,
    request: QueryRequest,
    response: Response,
    rate_limit_headers: Dict[str, str] = Depends(check_rate_limit)
):
    """
    Stream search results using Server-Sent Events with API key in the URL path.
    
    This endpoint follows the Model Context Protocol (MCP) for providing
    streaming search results that can be used as context for AI models.
    
    - **api_key**: WebCAT API key provided in the URL path for authentication
    - **query**: The search query to execute in the request body
    
    Returns a streaming response with search results.
    """
    async def event_generator() -> AsyncIterator[Dict[str, Any]]:
        try:
            query = request.query
            
            # Add rate limit headers to response
            for header_name, header_value in rate_limit_headers.items():
                response.headers[header_name] = header_value
            
            # Validate the WebCAT API key from URL
            if not api_key:
                logging.error("No WebCAT API key provided in URL path")
                yield {"event": "error", "data": "Authentication failed: No API key provided."}
                return
                
            # Validate against WEBCAT_API_KEY
            if api_key != WEBCAT_API_KEY:
                logging.error(f"Invalid WebCAT API key provided: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else '****'}")
                yield {"event": "error", "data": "Authentication failed: Invalid API key."}
                return
                
            logging.debug(f"Using provided API key from URL path")
            
            # After successful authentication, always use SERPER_API_KEY for search
            if not SERPER_API_KEY:
                logging.error("Server's SERPER_API_KEY is not configured")
                yield {"event": "error", "data": "Server configuration error: Search API key not configured."}
                return
                
            logging.info(f"MCP search stream with provided key: [{query}]")
            
            # Fetch search results using the server's SERPER_API_KEY
            results = fetch_search_results(query, SERPER_API_KEY)
            
            if not results:
                logging.warning(f"No search results found for query: {query}")
                yield {"event": "error", "data": "No search results found"}
                return
            
            # Send initial response with metadata
            yield {"event": "metadata", "data": {"query": query, "result_count": len(results)}}
            
            # Process and stream each result
            processed_results = process_search_results(results)
            
            for idx, result in enumerate(processed_results):
                # Artificial delay to simulate streaming behavior
                await asyncio.sleep(0.1)
                
                # Send each result as a separate event
                yield {"event": "result", "data": result.dict()}
                
            # Send completion event
            yield {"event": "done", "data": {"message": "All results sent"}}
                
        except Exception as e:
            logging.error(f"Search stream error: {str(e)}")
            yield {"event": "error", "data": f"Error: {str(e)}"}
    
    return EventSourceResponse(event_generator())

# RESTful search endpoint
@app.post("/search/{api_key}/rest")
async def search_with_key_rest(
    api_key: str,
    request: QueryRequest,
    response: Response,
    rate_limit_headers: Dict[str, str] = Depends(check_rate_limit)
):
    """
    Return search results as a standard JSON response with API key in the URL path.
    
    This endpoint provides a RESTful alternative to the SSE endpoint for getting
    search results that can be used as context for AI models.
    
    - **api_key**: WebCAT API key provided in the URL path for authentication
    - **query**: The search query to execute in the request body
    
    Returns a JSON response with search results.
    """
    try:
        query = request.query
        
        # Add rate limit headers to response
        for header_name, header_value in rate_limit_headers.items():
            response.headers[header_name] = header_value
        
        # Validate the WebCAT API key from URL
        if not api_key:
            logging.error("No WebCAT API key provided in URL path")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: No API key provided."
            )
            
        # Validate against WEBCAT_API_KEY
        if api_key != WEBCAT_API_KEY:
            logging.error(f"Invalid WebCAT API key provided: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else '****'}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Invalid API key."
            )
            
        logging.info(f"RESTful endpoint authenticated with valid WEBCAT_API_KEY")
        
        # After successful authentication, always use SERPER_API_KEY for search
        if not SERPER_API_KEY:
            logging.error("Server's SERPER_API_KEY is not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error: Search API key not configured."
            )
            
        logging.info(f"MCP RESTful search with provided key: [{query}]")
        
        # Fetch search results using the server's SERPER_API_KEY
        results = fetch_search_results(query, SERPER_API_KEY)
        
        if not results:
            logging.warning(f"No search results found for query: {query}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No search results found"
            )
        
        # Process results
        processed_results = process_search_results(results)
        
        # Prepare response data
        response_data = {
            "query": query,
            "result_count": len(processed_results),
            "results": [result.dict() for result in processed_results]
        }
        
        return SearchResponse(**response_data)
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"RESTful search error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

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
        "url": "https://github.com/Kode-Rex/webcat",
        "email": "t@koderex.dev"
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