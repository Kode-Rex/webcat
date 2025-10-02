# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""SearchResponse model - response from the search tool."""

from typing import List, Optional

from pydantic import BaseModel

from models.search_result import SearchResult


class SearchResponse(BaseModel):
    """Response from the search tool."""

    query: str
    search_source: str
    results: List[SearchResult]
    error: Optional[str] = None
