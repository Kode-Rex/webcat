# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""SearchResult model - represents a single search result with scraped content."""

from typing import Optional

from pydantic import BaseModel


class SearchResult(BaseModel):
    """Model for a single search result with scraped content."""

    title: str
    url: Optional[str] = ""
    snippet: str
    content: str = ""
