import json
import azure.functions as func
import logging
from readability.readability import Document
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urlparse

app = func.FunctionApp()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
]

def fetch_content(url, headers):
    response = requests.get(url, headers=headers)
    doc = Document(response.content)
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
            logging.error(f"Initial requests failed: {str(e)}")
            proxy_url = f"https://12ft.io/{url}"
            logging.info(f"Retrying with proxy: {proxy_url}")
            soup = fetch_content(proxy_url, headers)

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
            logging.error(f"Initial requests failed: {str(e)}")
            proxy_url = f"https://12ft.io/{url}"
            logging.info(f"Retrying with proxy: {proxy_url}")
            soup = fetch_content(proxy_url, headers)

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
