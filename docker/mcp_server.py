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
import html2text
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
    Scrapes the content of a search result URL and converts it to markdown.
    
    Args:
        result: SearchResult object with URL to scrape
        
    Returns:
        Updated SearchResult with content in markdown format
    """
    if not result.url:
        result.content = "Error: Missing URL for content scraping."
        return result
    
    try:
        # Add request headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        response = requests.get(result.url, timeout=5, headers=headers)
        response.raise_for_status()
        
        # Check content type to handle different file types
        content_type = response.headers.get('Content-Type', '').lower()
        
        # Handle plain text
        if 'text/plain' in content_type:
            result.content = f"# {result.title}\n\n*Source: {result.url}*\n\n```\n{response.text[:8000]}\n```"
            return result
            
        # Handle PDF and other binary formats
        if 'application/pdf' in content_type or 'application/octet-stream' in content_type:
            result.content = f"# {result.title}\n\n*Source: {result.url}*\n\n**Note:** This content appears to be a binary file ({content_type}) and cannot be converted to markdown. Please download the file directly from the source URL."
            return result
        
        # Use readability to extract the main content
        try:
            doc = Document(response.content)
            title = doc.title()
            
            # Convert HTML to Markdown using html2text
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0  # No wrapping
            h.unicode_snob = True  # Use Unicode instead of ASCII
            h.escape_snob = True  # Don't escape special chars
            h.use_automatic_links = True  # Auto-link URLs
            h.mark_code = True  # Use markdown syntax for code blocks
            h.single_line_break = False  # Use two line breaks to create a new paragraph
            h.table_border_style = "html"  # Use HTML table borders
            h.images_to_alt = False  # Include image URLs
            h.protect_links = True  # Don't convert links to references
            
            # Pre-process HTML to handle special elements
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            
            # Handle code blocks better - ensure they have language tags when possible
            for pre in soup.find_all('pre'):
                if pre.code and pre.code.get('class'):
                    classes = pre.code.get('class')
                    # Look for language classes like 'language-python', 'python', etc.
                    language = None
                    for cls in classes:
                        if cls.startswith(('language-', 'lang-')) or cls in ['python', 'javascript', 'css', 'html', 'java', 'php', 'c', 'cpp', 'csharp', 'ruby', 'go']:
                            language = cls.replace('language-', '').replace('lang-', '')
                            break
                    
                    if language:
                        # Wrap in markdown code fence with language
                        pre.insert_before(f'```{language}')
                        pre.insert_after('```')
            
            # Handle LaTeX/MathJax by preserving the markup
            for math in soup.find_all(['math', 'script']):
                if math.name == 'script' and math.get('type') in ['math/tex', 'math/tex; mode=display', 'application/x-mathjax-config']:
                    # Preserve math content
                    math.replace_with(f'$$${math.string}$$$')
                elif math.name == 'math':
                    # Preserve MathML
                    math.replace_with(f'$$${str(math)}$$$')
            
            # Get the markdown content
            markdown_text = h.handle(str(soup))
            
            # Add title and metadata at the beginning
            full_content = f"# {title}\n\n*Source: {result.url}*\n\n{markdown_text}"
            
        except Exception as e:
            # Fallback to direct HTML to Markdown conversion if readability fails
            logging.warning(f"Readability parsing failed: {str(e)}. Falling back to direct HTML parsing.")
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            title = title_tag.text if title_tag else result.title
            
            full_content = f"# {title}\n\n*Source: {result.url}*\n\n{h.handle(str(soup))}"
        
        # Limit content length to prevent huge responses
        if len(full_content) > 8000:
            full_content = full_content[:8000] + "... [content truncated]"
        
        result.content = full_content
        return result
    except requests.RequestException as e:
        result.content = f"Error: Failed to retrieve the webpage. {str(e)}"
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting FastMCP server on port {port}")
    
    # Run the server
    mcp_server.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port
    ) 