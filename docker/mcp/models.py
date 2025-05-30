"""Models for the MCP server."""

from typing import List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator

class QueryRequest(BaseModel):
    """Request model for search queries."""
    query: str = Field(..., description="The search query")

class ApiKeyRequest(BaseModel):
    """Request model for API key updates."""
    api_key: str = Field(..., description="API key for Serper")

class SearchResult(BaseModel):
    """Model for a single search result with content."""
    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    snippet: Optional[str] = Field(None, description="Snippet from the search result")
    content: str = Field(..., description="Scraped and processed content")

class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str = Field(..., description="The original search query")
    result_count: int = Field(..., description="Number of results returned")
    results: List[SearchResult] = Field(..., description="List of search results with content")
    
class ErrorResponse(BaseModel):
    """Standard error response model."""
    status_code: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Error message")
    error_type: str = Field("general_error", description="Type of error")
    details: Optional[Any] = Field(None, description="Additional error details") 