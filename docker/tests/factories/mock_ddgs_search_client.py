# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Typed mock for DDGS search client - no raw property assignment."""

from typing import Any, Dict, List, Optional


class MockDDGS:
    """Typed mock for DDGS search client."""

    def __init__(
        self,
        results: Optional[List[Dict[str, Any]]] = None,
        should_raise: Optional[Exception] = None,
    ):
        """Initialize mock DDGS.

        Args:
            results: List of search result dictionaries
            should_raise: Exception to raise when text() is called
        """
        self._results = results or []
        self._should_raise = should_raise
        self.text_called_with: Optional[tuple] = None

    def text(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Mock text search method.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of search result dictionaries

        Raises:
            Exception if should_raise was set
        """
        self.text_called_with = (query, max_results)

        if self._should_raise:
            raise self._should_raise

        return self._results
