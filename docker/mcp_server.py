import json
import logging
import random
import time
import os
import concurrent.futures
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
from readability import Document
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

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

# Configure logging
logging.basicConfig(level=logging.INFO)

# In-memory API key
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
]

# Model schemas
class QueryRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

class ApiKeyRequest(BaseModel):
    api_key: str

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    content: str

class SearchResponse(BaseModel):
    query: str
    result_count: int
    results: List[SearchResult]

# Helper functions
def fetch_content(url: str, headers: Dict[str, str]) -> BeautifulSoup:
    """Fetch and parse content from a URL using readability."""
    response = requests.get(url, headers=headers, timeout=10)
    html_content = response.content.decode(response.encoding or 'utf-8')
    doc = Document(html_content)
    summary_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, 'html.parser')
    return soup

def clean_text(text: str) -> str:
    """Clean scraped text by normalizing whitespace and newlines."""
    if not text:
        return ""
    # Replace multiple newlines with a single newline
    text = '\n'.join(line.strip() for line in text.splitlines() if line.strip())
    # Replace multiple spaces with a single space
    text = ' '.join(text.split())
    return text

def try_fetch_with_backoff(url: str, headers: Dict[str, str], attempts: int = 3, backoff_factor: int = 2) -> BeautifulSoup:
    """Try to fetch content with exponential backoff on failure."""
    for attempt in range(attempts):
        try:
            return fetch_content(url, headers)
        except Exception as e:
            if attempt < attempts - 1:
                sleep_time = backoff_factor * attempt + random.uniform(0, 2)
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error(f"All attempts failed: {str(e)}")
                raise

# MCP specific preprocessing for page content
def mcp_process_content(content: str) -> str:
    """
    Process content for MCP - simplified to just basic cleaning.
    """
    # Basic cleaning only
    return clean_text(content)

# Function to scrape content from a single search result
def scrape_search_result(result: Dict[str, Any]) -> SearchResult:
    """Scrape content from a single search result URL."""
    url = result.get('link')
    if not url:
        return SearchResult(
            title=result.get('title', 'Untitled'),
            url="",
            snippet=result.get('snippet', ''),
            content="Error: Missing URL"
        )
        
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent}
    
    try:
        soup = try_fetch_with_backoff(url, headers)
        raw_content = soup.get_text(separator=' ').strip()
        
        # Process content
        content = mcp_process_content(raw_content)
        
        return SearchResult(
            title=result.get('title', 'Untitled'),
            url=url,
            snippet=result.get('snippet', ''),
            content=content
        )
    except Exception as e:
        logging.error(f"Failed to scrape {url}: {str(e)}")
        return SearchResult(
            title=result.get('title', 'Untitled'),
            url=url,
            snippet=result.get('snippet', ''),
            content=f"Error: Failed to scrape content - {str(e)}"
        )

# Endpoints
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
        
        # Call Serper.dev API to get search results
        serper_url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'q': query,
            'gl': 'us',
            'hl': 'en'
        }
        
        response = requests.post(serper_url, headers=headers, json=payload)
        search_results = response.json()
        
        # Extract top results
        if 'organic' not in search_results or not search_results['organic']:
            raise HTTPException(status_code=404, detail="No search results found")
            
        top_results = search_results['organic'][:3]
        
        # Use ThreadPoolExecutor to parallelize scraping operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(top_results)) as executor:
            # Submit all scraping tasks
            future_to_result = {
                executor.submit(scrape_search_result, result): result 
                for result in top_results
            }
            
            # Collect results as they complete
            results_with_content = []
            for future in concurrent.futures.as_completed(future_to_result):
                results_with_content.append(future.result())
        
        # Return response
        return SearchResponse(
            query=query,
            result_count=len(results_with_content),
            results=results_with_content
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Run the server with uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=port, reload=False) 