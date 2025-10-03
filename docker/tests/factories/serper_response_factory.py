# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Factory for creating Serper API response test doubles."""

from typing import Any, Dict, List

from tests.factories.mock_serper_response import MockSerperResponse


class SerperResponseFactory:
    """Factory for creating pre-configured Serper API response mocks."""

    @staticmethod
    def with_results(results: List[Dict[str, Any]]) -> MockSerperResponse:
        """Create response with organic search results.

        Args:
            results: List of result dictionaries with title, link, snippet

        Returns:
            MockSerperResponse with organic results
        """
        return MockSerperResponse(organic_results=results)

    @staticmethod
    def empty() -> MockSerperResponse:
        """Create response with no organic results.

        Returns:
            MockSerperResponse with empty organic array
        """
        return MockSerperResponse(organic_results=[])

    @staticmethod
    def two_results() -> MockSerperResponse:
        """Create response with two example results.

        Returns:
            MockSerperResponse with two pre-configured results
        """
        return MockSerperResponse(
            organic_results=[
                {
                    "title": "Result 1",
                    "link": "https://example.com/1",
                    "snippet": "Snippet 1",
                },
                {
                    "title": "Result 2",
                    "link": "https://example.com/2",
                    "snippet": "Snippet 2",
                },
            ]
        )

    @staticmethod
    def with_missing_fields() -> MockSerperResponse:
        """Create response with results missing optional fields.

        Returns:
            MockSerperResponse with incomplete result data
        """
        return MockSerperResponse(
            organic_results=[
                {
                    "title": "Title Only Result",
                    "link": "https://example.com/incomplete",
                    # Missing snippet
                }
            ]
        )
