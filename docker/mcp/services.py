"""Services for the MCP server."""

import logging
import random
import concurrent.futures
from typing import Dict, List, Any

import requests

from .models import SearchResult
from .utils import USER_AGENTS, try_fetch_with_backoff, mcp_process_content

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

def fetch_search_results(query: str, api_key: str) -> List[Dict[str, Any]]:
    """Fetch search results from Serper API."""
    serper_url = "https://google.serper.dev/search"
    
    # Detailed logging of API key
    if not api_key:
        logging.error("API key is empty or None")
        return []
    
    logging.debug(f"API key length: {len(api_key)}")
    logging.debug(f"API key first 4 chars: {api_key[:4] if len(api_key) >= 4 else 'too short'}")
    logging.debug(f"API key last 4 chars: {api_key[-4:] if len(api_key) >= 4 else 'too short'}")
    
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    logging.debug(f"Full headers being sent: {headers}")
    
    payload = {
        'q': query,
        'gl': 'us',
        'hl': 'en'
    }
    
    logging.debug(f"Full payload being sent: {payload}")
    
    try:
        logging.debug("Sending request to Serper API...")
        response = requests.post(serper_url, headers=headers, json=payload)
        logging.debug(f"Response status code: {response.status_code}")
        logging.debug(f"Response headers: {response.headers}")
        
        # Log response content for debugging
        try:
            if response.status_code != 200:
                logging.error(f"Error response content: {response.text}")
            else:
                logging.debug("Response received successfully")
        except Exception as e:
            logging.error(f"Error reading response content: {str(e)}")
            
        response.raise_for_status()  # Raise exception for 4XX/5XX status codes
        search_results = response.json()
        
        if 'organic' not in search_results or not search_results['organic']:
            logging.warning(f"No organic results found in Serper API response for query: {query}")
            return []
            
        return search_results['organic'][:3]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Serper API: {str(e)}")
        return []

def process_search_results(results: List[Dict[str, Any]]) -> List[SearchResult]:
    """Process search results in parallel."""
    # Use ThreadPoolExecutor to parallelize scraping operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(results)) as executor:
        # Submit all scraping tasks
        future_to_result = {
            executor.submit(scrape_search_result, result): result 
            for result in results
        }
        
        # Collect results as they complete
        processed_results = []
        for future in concurrent.futures.as_completed(future_to_result):
            processed_results.append(future.result())
    
    return processed_results 