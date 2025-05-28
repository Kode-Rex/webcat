import json
import azure.functions as func
import logging
from readability import Document
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# In-memory API key (fallback if environment variable is not set)
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "")

app = func.FunctionApp()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
]

def fetch_content(url, headers):
    response = requests.get(url, headers=headers)
    html_content = response.content.decode(response.encoding or 'utf-8')
    doc = Document(html_content)
    summary_html = doc.summary(html_partial=True)
    soup = BeautifulSoup(summary_html, 'html.parser')
    return soup

def try_fetch_with_backoff(url, headers, attempts=3, backoff_factor=2):
    for attempt in range(attempts):
        try:
            return fetch_content(url, headers)
        except Exception as e:
            if attempt < attempts - 1:  # No sleep after the last attempt
                sleep_time = backoff_factor * attempt + random.uniform(0, 2)
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
            else:
                logging.error(f"All attempts failed: {str(e)}")
                raise

@app.route(route="scrape", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def scrape(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        url = data.get('url')

        if not url:
            return func.HttpResponse("Error: Missing URL", status_code=400)

        logging.info(f'scrape [{url}]')

        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            soup = try_fetch_with_backoff(url, headers)
        except Exception as e:
            logging.error(f"Requests failed: {str(e)}")
            return func.HttpResponse(f"Error: Failed to scrape the URL - {str(e)}", status_code=500)

        content = soup.get_text(separator='\n').strip()

        return func.HttpResponse(content, mimetype="text/plain")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: Failed to scrape the URL - {str(e)}", status_code=500)

@app.route(route="scrape_with_images", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def scrape_with_images(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        url = data.get('url')

        if not url:
            return func.HttpResponse("Error: Missing URL", status_code=400)

        logging.info(f'scraping_with_images [{url}]')

        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            soup = try_fetch_with_backoff(url, headers)
        except Exception as e:
            logging.error(f"Requests failed: {str(e)}")
            return func.HttpResponse(f"Error: Failed to scrape the URL - {str(e)}", status_code=500)

        content = ''
        for element in soup.descendants:
            if isinstance(element, str):
                content += element.strip() + '\n'
            elif element.name == 'img':
                img_url = element.get('src')
                if img_url and img_url.startswith(('http://', 'https://')):
                    content += f'\n{img_url}\n'

        content = content.strip()

        response_data = {
            "content": content
        }

        return func.HttpResponse(json.dumps(response_data), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: Failed to scrape the URL - {str(e)}", status_code=500)

@app.route(route="set_api_key", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def set_api_key(req: func.HttpRequest) -> func.HttpResponse:
    try:
        global SERPER_API_KEY
        data = req.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return func.HttpResponse("Error: Missing API key", status_code=400)
            
        # Set the API key in memory
        SERPER_API_KEY = api_key
        
        return func.HttpResponse("API key set successfully", status_code=200)
    except Exception as e:
        logging.error(f"Error setting API key: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)

@app.route(route="search", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def search(req: func.HttpRequest) -> func.HttpResponse:
    try:
        global SERPER_API_KEY
        data = req.get_json()
        query = data.get('query')
        
        # Use the in-memory API key, or allow overriding with a request parameter
        api_key = data.get('api_key') or SERPER_API_KEY
        
        if not query:
            return func.HttpResponse("Error: Missing search query", status_code=400)
        
        if not api_key:
            return func.HttpResponse("Error: Serper API key not configured. Please use the /api/set_api_key endpoint first.", status_code=400)
            
        logging.info(f'search [{query}]')
        
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
        
        # Extract top 3 organic results
        if 'organic' not in search_results or not search_results['organic']:
            return func.HttpResponse("No search results found", status_code=404)
            
        top_results = search_results['organic'][:3]
        results_with_content = []
        
        user_agent = random.choice(USER_AGENTS)
        headers = {'User-Agent': user_agent}
        
        # Scrape content for each result
        for result in top_results:
            url = result.get('link')
            if not url:
                continue
                
            try:
                # Use the existing scrape functionality
                soup = try_fetch_with_backoff(url, headers)
                content = soup.get_text(separator='\n').strip()
                
                results_with_content.append({
                    'title': result.get('title'),
                    'url': url,
                    'snippet': result.get('snippet'),
                    'content': content
                })
            except Exception as e:
                logging.error(f"Failed to scrape {url}: {str(e)}")
                results_with_content.append({
                    'title': result.get('title'),
                    'url': url,
                    'snippet': result.get('snippet'),
                    'content': f"Error: Failed to scrape content - {str(e)}"
                })
        
        # Include the query and result count in the response
        return func.HttpResponse(
            json.dumps({
                "query": query,
                "result_count": len(results_with_content),
                "results": results_with_content
            }),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
