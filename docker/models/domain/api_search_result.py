# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""APISearchResult model - raw search result from external APIs."""

from pydantic import BaseModel


class APISearchResult(BaseModel):
    """Raw search result from external API (Serper/DuckDuckGo)."""

    title: str
    link: str
    snippet: str

    class Config:
        """Pydantic config."""

        # Allow both 'link', 'url', and 'href' for compatibility
        extra = "allow"
