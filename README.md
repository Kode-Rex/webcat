# Web Cat API

## Introduction

Web Cat is a collection of Python-based APIs designed to enhance AI models with web search and content extraction capabilities. The project includes:

1. A serverless Python-based API hosted on Azure Functions
2. A Model Context Protocol (MCP) server that provides web search capabilities for AI models

Both implementations are designed to responsibly scrape and process website content, making it easy to integrate web content into AI applications like ChatGPT through Custom GPTs.

## Components

### Azure Functions API

The Azure Functions API leverages the readability library and BeautifulSoup to extract the main body of text and related images from web pages.

### MCP Server

The Model Context Protocol (MCP) server is a FastAPI-based implementation that provides web search capabilities with enhanced content extraction. It follows the MCP specification for standardized AI model interactions.

## Features
 - **Content Extraction**: Utilizes the readability library for clean text extraction
 - **Text Processing**: Further processes extracted content for improved usability
 - **Search Functionality**: Integrates with Serper.dev to provide web search capabilities
 - **MCP Compliance**: Follows standardized Model Context Protocol specifications
 - **Rate Limiting**: Protects the API from abuse with configurable rate limits
 - **API Versioning**: Ensures backward compatibility as the API evolves

## Getting Started

For the Azure Functions API:
- See the `customgpt` directory for specific documentation

For the MCP Server:
- See the `docker` directory for build and deployment instructions

## Limitations and Considerations
- **Text-Based Content**: The APIs are optimized for text and image content and may not accurately represent other multimedia or dynamic web content.
- **API Keys**: A Serper API key is required for search functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.

## Usage

Here's a quick example of how to test the API locally:

```bash
cd src
func start
curl -X POST http://localhost:7071/api/scrape -H "Content-Type: application/json" -d "{\"url\":\"https://example.com\"}" # text only
curl -X POST http://localhost:7071/api/scrape_with_images -H "Content-Type: application/json" -d "{\"url\":\"https://bigmedium.com/speaking/sentient-design-josh-clark-talk.html\"}" #text and images
curl -X POST http://localhost:7071/api/set_api_key -H "Content-Type: application/json" -d "{\"api_key\":\"your_serper_api_key\"}" # set Serper API key
curl -X POST http://localhost:7071/api/search -H "Content-Type: application/json" -d "{\"query\":\"your search query\"}" # search and get content
```
