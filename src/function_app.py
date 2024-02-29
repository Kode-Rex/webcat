import azure.functions as func
import logging
from readability.readability import Document
import requests
from bs4 import BeautifulSoup
import random
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

app = func.FunctionApp()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
]

def can_fetch(url):
    parsed_url = urlparse(url)
    url_root = f'{parsed_url.scheme}://{parsed_url.netloc}/'
    robots_url = f'{url_root}robots.txt'
    rp = RobotFileParser()

    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch("*", url)
        else:
            return True
    except Exception as e:
        logging.error("Exception in can_fetch: " + str(e))
        return f'Error fetching robots.txt: {e}'

@app.route(route="scrape", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def scrape(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        data = req.get_json()
        url = data.get('url')
        respect_robots_txt = data.get('respect_robots_txt', True)  # Default to True if not specified
        
        if not url:
            return func.HttpResponse("Error: Missing URL", status_code=400)
        
        if respect_robots_txt and not can_fetch(url):
            return func.HttpResponse("Error: Access denied by robots.txt", status_code=403)
        
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)
        doc = Document(response.content)
        summary_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary_html, 'html.parser')
        content = soup.get_text(separator='\n').strip()  # Added strip() here
        
        return func.HttpResponse(content, mimetype="text/plain")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: Failed to scrape the URL - {str(e)}", status_code=500)
