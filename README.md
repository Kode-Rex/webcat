# Web Cat API

## Introduction

Web Cat is a serverless Python-based API hosted on Azure Functions, designed to scrape and process website content responsibly. Leveraging the readability library and BeautifulSoup, Web Cat extracts the main body of text from web pages, making it easy to integrate website content ChatGPT through the use of Custom GPTs. This API respects robots.txt rules to ensure ethical web scraping practices.

Using the `@Web Cat` GPT enhances ideation by seamlessly integrating web content into conversations, eliminating the need for manual copy-pasting.

## Features
 - **Content Extraction**: Utilizes the readability library for clean text extraction.
 - **Text Processing**: Further processes extracted content for improved usability.

## Getting Started

### Prerequisites

- Azure Functions Core Tools
- Python 3.8 or later
- An Azure account and subscription

## Local Development

Prepare your local environment by running:

```bash
cd src
pip install -r requirements.txt
func start
```

## Limitations and Considerations
- **Text-Based Content**: The API is optimized for text content and may not accurately represent multimedia or dynamic web content.

## Usage

Here's a quick example of how to test the API locally:

```bash
cd src
func start
curl -X POST http://localhost:7071/api/scrape -H "Content-Type: application/json" -d "{\"url\":\"https://example.com\"}"
```
