# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""API response models for FastMCP WebCat integration."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class APISearchToolResponse(BaseModel):
    """Response from API search tool with additional metadata."""

    success: bool
    query: str
    max_results: int
    search_source: str
    results: List[Dict[str, Any]]  # SearchResult dicts
    total_found: int
    note: str = ""
    error: Optional[str] = None


class APIHealthCheckResponse(BaseModel):
    """Response from API health check tool."""

    success: bool
    status: str
    service: str
    error: Optional[str] = None


class APIServerInfoResponse(BaseModel):
    """Response from API server info tool."""

    success: bool
    version: str
    server: str
    features: List[str]
    error: Optional[str] = None


class APIScrapeResponse(BaseModel):
    """Response from API scrape tool."""

    success: bool
    url: str
    title: str
    content: str
    error: Optional[str] = None
