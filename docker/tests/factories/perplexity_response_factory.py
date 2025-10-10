# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Factory for creating Perplexity response test doubles."""

from typing import List

from tests.factories.mock_perplexity_response import (
    MockPerplexityClient,
    MockPerplexityResponse,
)


class PerplexityResponseFactory:
    """Factory for creating pre-configured Perplexity response mocks."""

    @staticmethod
    def successful_research(
        content: str = "Python is a high-level programming language.",
        citations: List[str] = None,
    ) -> MockPerplexityResponse:
        """Create successful deep research response.

        Args:
            content: Research report content
            citations: Citation URLs

        Returns:
            MockPerplexityResponse with research content
        """
        if citations is None:
            citations = ["https://python.org", "https://docs.python.org"]
        return MockPerplexityResponse(content=content, citations=citations)

    @staticmethod
    def empty_response() -> MockPerplexityResponse:
        """Create empty response with no content.

        Returns:
            MockPerplexityResponse with empty choices
        """
        return MockPerplexityResponse(content="")

    @staticmethod
    def with_many_citations(num_citations: int = 10) -> MockPerplexityResponse:
        """Create response with many citations for testing max_results.

        Args:
            num_citations: Number of citations to include

        Returns:
            MockPerplexityResponse with specified number of citations
        """
        citations = [f"https://url{i}.com" for i in range(1, num_citations + 1)]
        return MockPerplexityResponse(
            content="Research with many sources", citations=citations
        )

    @staticmethod
    def without_citations() -> MockPerplexityResponse:
        """Create response without any citations.

        Returns:
            MockPerplexityResponse with no citations
        """
        return MockPerplexityResponse(
            content="Research without citations", citations=[]
        )

    @staticmethod
    def api_error() -> Exception:
        """Create API error exception.

        Returns:
            Exception to be used with side_effect
        """
        return Exception("API Error")

    @staticmethod
    def client_with_response(response: MockPerplexityResponse) -> MockPerplexityClient:
        """Create mock client that returns specific response.

        Args:
            response: Response to return from API calls

        Returns:
            MockPerplexityClient configured with response
        """
        return MockPerplexityClient(response)
