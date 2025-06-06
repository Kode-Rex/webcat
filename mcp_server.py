"""Entry point for the WebCat server using FastMCP."""

import os
import tempfile
from dotenv import load_dotenv
from fastmcp import FastMCP
import uvicorn
import logging
from logging.handlers import RotatingFileHandler

# Set up logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = os.environ.get("LOG_DIR", tempfile.gettempdir())
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

# Load environment variables
load_dotenv()

# Import necessary modules for search functionality
import requests
from bs4 import BeautifulSoup
from readability import Document
import json
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Model definitions
class SearchResult(BaseModel):
    """Model for a search result."""
    title: str
    url: Optional[str] = ""
    snippet: str
    content: str = ""

# Configure API keys
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")
WEBCAT_API_KEY = os.environ.get("WEBCAT_API_KEY", "")

# Improved logging for API keys
if WEBCAT_API_KEY:
    key_length = len(WEBCAT_API_KEY)
    masked_key = WEBCAT_API_KEY[:4] + "*" * (key_length - 8) + WEBCAT_API_KEY[-4:] if key_length > 8 else "****"
    logging.info(f"WEBCAT_API_KEY is set (masked: {masked_key})")
else:
    logging.warning("WEBCAT_API_KEY is not set! Authentication will not work.")

logging.info(f"Using SERPER API key from environment: {'Set' if SERPER_API_KEY else 'Not set'}")

# Create FastMCP instance
mcp_server = FastMCP(
    name="WebCat Search",
    description="A server providing web search capabilities to models following the MCP protocol",
    version="1.0.0",
    authentication_key=WEBCAT_API_KEY
)

# Utility functions
def fetch_search_results(query: str, api_key: str) -> List[Dict[str, Any]]:
    """
    Fetches search results from the Serper API.
    
    Args:
        query: The search query
        api_key: The Serper API key
        
    Returns:
        A list of search result dictionaries
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        
        # Process and return the search results
        if 'organic' in data:
            return data['organic']
        return []
    except Exception as e:
        logging.error(f"Error fetching search results: {str(e)}")
        return []

def scrape_search_result(result: SearchResult) -> SearchResult:
    """
    Scrapes the content of a search result URL.
    
    Args:
        result: SearchResult object with URL to scrape
        
    Returns:
        Updated SearchResult with content
    """
    if not result.url:
        result.content = "Error: Missing URL for content scraping."
        return result
    
    try:
        response = requests.get(result.url, timeout=5)
        response.raise_for_status()
        
        # Use readability to extract the main content
        doc = Document(response.content)
        
        # Extract text from HTML
        soup = BeautifulSoup(doc.summary(), 'html.parser')
        result.content = soup.get_text(separator="\n").strip()
        
        # Limit content length to prevent huge responses
        if len(result.content) > 8000:
            result.content = result.content[:8000] + "... [content truncated]"
            
        return result
    except Exception as e:
        result.content = f"Error: Failed to scrape content. {str(e)}"
        return result

def process_search_results(results: List[Dict[str, Any]]) -> List[SearchResult]:
    """
    Processes raw search results into SearchResult objects with content.
    
    Args:
        results: List of raw search result dictionaries
        
    Returns:
        List of SearchResult objects with scraped content
    """
    processed_results = []
    
    for result in results:
        # Create a SearchResult object
        search_result = SearchResult(
            title=result.get('title', 'Untitled'),
            url=result.get('link', ''),
            snippet=result.get('snippet', '')
        )
        
        # Scrape content for the result
        search_result = scrape_search_result(search_result)
        processed_results.append(search_result)
    
    return processed_results

# Create a search tool
@mcp_server.tool(
    name="search",
    description="Search the web for information",
)
async def search_tool(query: str, ctx=None):
    """Search the web for information on a given query."""
    logging.info(f"Processing search request: {query}")
    
    # Check if Serper API key is configured
    if not SERPER_API_KEY:
        logging.error("Server's SERPER_API_KEY is not configured")
        return {"error": "Search API key not configured on the server."}
    
    # Fetch and process search results
    results = fetch_search_results(query, SERPER_API_KEY)
    if not results:
        logging.warning(f"No search results found for query: {query}")
        return {"error": "No search results found."}
    
    # Process the results
    processed_results = process_search_results(results)
    
    # Return formatted results
    return {
        "query": query,
        "results": [result.model_dump() for result in processed_results]
    }

# Create a simple health check tool
@mcp_server.tool(
    name="health_check",
    description="Check the health of the server"
)
async def health_check():
    """Check the health of the server."""
    return {"status": "healthy", "service": "webcat"}

# Get the starlette app
app = mcp_server.http_app().app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting FastMCP server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port) 