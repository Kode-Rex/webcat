# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Fluent builder for APISearchResult test objects."""

from models.api_search_result import APISearchResult


class APISearchResultBuilder:
    """
    Fluent builder for creating APISearchResult test objects.

    Usage:
        result = (an_api_search_result()
                  .with_title("My Article")
                  .with_link("https://example.com")
                  .with_snippet("A great article about...")
                  .build())
    """

    def __init__(self):
        self._title = "Test Title"
        self._link = "https://example.com"
        self._snippet = "Test snippet"

    def with_title(self, title: str) -> "APISearchResultBuilder":
        """Set the title."""
        self._title = title
        return self

    def with_link(self, link: str) -> "APISearchResultBuilder":
        """Set the link."""
        self._link = link
        return self

    def with_snippet(self, snippet: str) -> "APISearchResultBuilder":
        """Set the snippet."""
        self._snippet = snippet
        return self

    def build(self) -> APISearchResult:
        """Build the APISearchResult instance."""
        return APISearchResult(
            title=self._title,
            link=self._link,
            snippet=self._snippet,
        )


def an_api_search_result() -> APISearchResultBuilder:
    """Entry point for creating APISearchResult builders."""
    return APISearchResultBuilder()


def a_serper_result() -> APISearchResultBuilder:
    """Pre-configured builder for Serper API results."""
    return (
        APISearchResultBuilder()
        .with_title("Serper Result")
        .with_link("https://serper.example.com")
        .with_snippet("Result from Serper API")
    )


def a_duckduckgo_result() -> APISearchResultBuilder:
    """Pre-configured builder for DuckDuckGo results."""
    return (
        APISearchResultBuilder()
        .with_title("DuckDuckGo Result")
        .with_link("https://duckduckgo.example.com")
        .with_snippet("Result from DuckDuckGo")
    )
