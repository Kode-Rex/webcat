"""Utility functions for the MCP server."""

import logging
import random
import time
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup
from readability import Document

# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/18.19041",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
]

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

def mcp_process_content(content: str) -> str:
    """
    Process content for MCP - simplified to just basic cleaning.
    """
    # Basic cleaning only
    return clean_text(content) 