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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
]

@app.route(route="scrape", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def scrape(req: func.HttpRequest) -> func.HttpResponse:
    
    
    try:
        data = req.get_json()
        url = data.get('url')
        
        if not url:
            return func.HttpResponse("Error: Missing URL", status_code=400)
        
        logging.info(f'scrape [{url}]')
        
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


@app.route(route="scrape_with_images", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def scrape_with_images(req: func.HttpRequest) -> func.HttpResponse:

    try:
        data = req.get_json()
        url = data.get('url')
        
        if not url:
            return func.HttpResponse("Error: Missing URL", status_code=400)
        
        logging.info(f'scraping_with_images [{url}]')
        
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers)
        doc = Document(response.content)
        summary_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(summary_html, 'html.parser')
        content = soup.get_text(separator='\n').strip()  

        # Extract images
        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src')
            if img_url and img_url.startswith(('http://', 'https://')):
                images.append(img_url)
        
        response_data = {
            "content": content,
            "images": images
        }
        
        return func.HttpResponse(json.dumps(response_data), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: Failed to scrape the URL - {str(e)}", status_code=500)
