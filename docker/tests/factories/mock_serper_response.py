# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Typed mock for Serper API responses - no raw property assignment."""

from typing import Any, Dict, List, Optional


class MockSerperResponse:
    """Typed mock for Serper API HTTP responses."""

    def __init__(
        self,
        organic_results: Optional[List[Dict[str, Any]]] = None,
        status_code: int = 200,
    ):
        """Initialize mock Serper response.

        Args:
            organic_results: List of organic search results
            status_code: HTTP status code
        """
        self.status_code = status_code
        self._json_data = {"organic": organic_results or []}

    def json(self) -> Dict[str, Any]:
        """Return JSON response data."""
        return self._json_data

    def raise_for_status(self):
        """Raise HTTPError if status code indicates error."""
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"{self.status_code} Error")
