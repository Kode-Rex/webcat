# Model Context Protocol (MCP) Server

This directory contains the FastAPI-based Model Context Protocol (MCP) server that provides web search capabilities for AI models.

## Features

- Web search with content extraction
- Parallel processing of search results for faster response times
- Serper API integration for high-quality search results
- FastAPI-powered with OpenAPI documentation
- Containerized for easy deployment
- MCP-compliant API design
- API versioning for backward compatibility
- Rate limiting to prevent abuse
- Consistent error handling
- Enhanced documentation

## Prerequisites

- Docker
- Docker Compose (optional, for local development)
- Serper API key (required for search functionality)

## Code Structure

The server code is organized into a clean, modular structure:

- `mcp/app.py` - Main FastAPI application and route definitions
- `mcp/models.py` - Pydantic models for request/response validation
- `mcp/services.py` - Core business logic for web search and content extraction
- `mcp/utils.py` - Utility functions and helper classes

## Configuration

The MCP server can be configured using environment variables:

### Environment Variables

- `SERPER_API_KEY`: Your Serper API key for web search functionality
- `PORT`: The port on which the MCP server will run (default: 8000)
- `RATE_LIMIT_WINDOW`: Time window in seconds for rate limiting (default: 60)
- `RATE_LIMIT_MAX_REQUESTS`: Maximum number of requests allowed in the time window (default: 10)

### Setting Environment Variables

When using Docker Compose:

```bash
# Set your Serper API key
export SERPER_API_KEY=your_serper_api_key

# Optionally, set a custom port (default is 8000)
export PORT=9000

# Start the container
docker-compose up
```

When using Docker directly:

```bash
docker run -p 9000:9000 -e SERPER_API_KEY=your_serper_api_key -e PORT=9000 webcat:latest
```

## Building the Docker Image

You can build the Docker image using the provided build script:

```bash
# Make the build script executable if needed
chmod +x build.sh

# Run the build script
./build.sh
```

This will create a Docker image tagged with the current date/time and also as `latest`.

## Running with Docker Compose

For local development and testing, you can use Docker Compose:

```bash
# Set your Serper API key as an environment variable
export SERPER_API_KEY=your_serper_api_key

# Start the container
docker-compose up
```

## Running with Docker

You can also run the container directly with Docker:

```bash
docker run -p 8000:8000 -e SERPER_API_KEY=your_serper_api_key webcat:latest
```

## API Endpoints

The container exposes the following API endpoints:

- `POST /api/v1/set_api_key` - Set the Serper API key
- `POST /api/v1/search` - Search the web and return results with enhanced content
- `GET /health` - Health check endpoint
- `GET /docs` - FastAPI automatic API documentation

## Example Usage

### Set API Key

```bash
curl -X POST http://localhost:8000/api/v1/set_api_key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_serper_api_key"}'
```

### Search the Web

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "latest AI developments"}'
```

### View API Documentation

Open your browser and navigate to `http://localhost:8000/docs` to view the interactive API documentation provided by FastAPI's Swagger UI.

## Rate Limiting

The server implements rate limiting to prevent abuse:

- Default: 10 requests per 60-second window per IP address
- When rate limit is exceeded, the server returns a 429 status code
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed in the window
  - `X-RateLimit-Remaining`: Remaining requests in the current window
  - `X-RateLimit-Reset`: Seconds until the window resets

## Testing

The MCP server includes a comprehensive test suite to ensure functionality. The tests cover:

- Web search functionality
- Parallel processing of search results
- Error handling
- API key validation
- Health check endpoint
- Rate limiting

### Running Tests

To run the tests locally:

```bash
# Navigate to the tests directory
cd docker/tests

# Make the test script executable if needed
chmod +x run_tests.sh

# Run the tests
./run_tests.sh
```

The test script will install any necessary dependencies and run the tests with coverage reporting. 