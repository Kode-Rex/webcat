"""FastAPI application for the MCP server."""

import logging
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .models import QueryRequest, SearchResponse, SearchResult
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
    description="A server for providing search context to models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcp"}
 
@app.post("/api/search", response_model=SearchResponse)
def search(request: QueryRequest):
    """Search the web and return results with content."""
    try:
        global SERPER_API_KEY
        query = request.query
        
        # Use the in-memory API key, or allow overriding with a request parameter
        api_key = request.api_key or SERPER_API_KEY
        
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="Serper API key not configured. Please provide an api_key in the request."
            )
            
        logging.info(f'MCP search: [{query}]')
        
        # Fetch search results
        results = fetch_search_results(query, api_key)
        
        if not results:
            raise HTTPException(status_code=404, detail="No search results found")
        
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
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Entry point for running with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("mcp.app:app", host="0.0.0.0", port=port, reload=False) 