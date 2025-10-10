# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Typed mock for Perplexity API responses."""

from typing import List, Optional


class MockPerplexityMessage:
    """Typed mock for Perplexity message object."""

    def __init__(self, content: str):
        """Initialize message with content.

        Args:
            content: Message content (research report)
        """
        self.content = content


class MockPerplexityChoice:
    """Typed mock for Perplexity choice object."""

    def __init__(self, content: str):
        """Initialize choice with message content.

        Args:
            content: Message content
        """
        self.message = MockPerplexityMessage(content)


class MockPerplexityUsage:
    """Typed mock for Perplexity usage stats."""

    def __init__(self, total_tokens: int = 1000):
        """Initialize usage stats.

        Args:
            total_tokens: Total token count
        """
        self.total_tokens = total_tokens


class MockPerplexityResponse:
    """Typed mock for Perplexity API completion response."""

    def __init__(
        self,
        content: str = "",
        citations: Optional[List[str]] = None,
        total_tokens: int = 1000,
    ):
        """Initialize mock Perplexity response.

        Args:
            content: Research report content
            citations: List of citation URLs
            total_tokens: Total tokens used
        """
        self.choices = [MockPerplexityChoice(content)] if content else []
        self.citations = citations or []
        self.usage = MockPerplexityUsage(total_tokens)


class MockPerplexityClient:
    """Typed mock for Perplexity client."""

    def __init__(self, response: MockPerplexityResponse):
        """Initialize mock client with predefined response.

        Args:
            response: Response to return from API calls
        """
        self._response = response
        self.chat = self
        self.completions = self

    def create(self, **kwargs) -> MockPerplexityResponse:
        """Mock create method that returns configured response.

        Returns:
            Configured MockPerplexityResponse
        """
        return self._response
