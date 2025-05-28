# Web Cat API

## Introduction

Web Cat is a serverless Python-based API hosted on Azure Functions, designed to scrape and process website content responsibly. Leveraging the readability library and BeautifulSoup, `Web Cat` extracts the main body of text and related images from web pages, making it easy to integrate website content ChatGPT through the use of Custom GPTs. 

Using the `@Web Cat` GPT enhances ideation by seamlessly integrating web content into conversations, eliminating the need for manual copy-pasting or suffering through out dated data issues. 

## Features
 - **Content Extraction**: Utilizes the readability library for clean text extraction.
 - **Text Processing**: Further processes extracted content for improved usability.

## Getting Started

### Prerequisites

- Azure Functions Core Tools
- Python 3.11
- An Azure account and subscription

## Local Development

Prepare your local environment by running:

```bash
cd src
pip install -r requirements.txt
func start
```

## Limitations and Considerations
- **Text-Based Content**: The API is optimized for text and image content and may not accurately represent other multimedia or dynamic web content.

## Usage

Here's a quick example of how to test the API locally:

```bash
cd src
func start
curl -X POST http://localhost:7071/api/scrape -H "Content-Type: application/json" -d "{\"url\":\"https://example.com\"}" # text only
curl -X POST http://localhost:7071/api/scrape_with_images -H "Content-Type: application/json" -d "{\"url\":\"https://bigmedium.com/speaking/sentient-design-josh-clark-talk.html\"}" #text and images
```

## TODO

### Search API Integration

- [ ] Integrate with [Serper.dev](https://serper.dev/) search API to provide search functionality
- [ ] Develop a search endpoint that:
  - Fetches search results using Serper API
  - Processes and filters results for relevance
  - Automatically scrapes top relevant pages
  - Returns a combined response with search results and page content
- [ ] Create appropriate rate limiting and caching strategies
- [ ] Add authentication for search functionality
- [ ] Update documentation with search API usage examples
