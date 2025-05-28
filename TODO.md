# WebCat Project TODOs

## Completed
- [x] Set up proper virtual environment for Azure Functions
- [x] Install required dependencies in Python 3.11 (compatible with Azure Functions runtime)
- [x] Fix readability module import issue
- [x] Fix text encoding/decoding in the content scraping
- [x] Add clean_text function to normalize and format scraped text
- [x] Remove 12ft.io fallback from scraping functions
- [x] Create search endpoint using Serper.dev API
- [x] Add API key management functionality
- [x] Add result count in search response

## Todo
- [ ] Add error handling for different HTTP status codes from source websites
- [ ] Implement caching mechanism for frequently accessed content
- [ ] Add rate limiting for API endpoints
- [ ] Create documentation for all API endpoints
- [ ] Add tests for each function
- [ ] Implement logging improvements for better debugging
- [ ] Add configuration options for search parameters (country, language)
- [ ] Create a frontend interface for the API 