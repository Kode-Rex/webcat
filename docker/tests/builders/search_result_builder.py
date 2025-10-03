# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Fluent builder for SearchResult test objects."""

from models.search_result import SearchResult


class SearchResultBuilder:
    """
    Fluent builder for creating SearchResult test objects.

    Usage:
        result = (a_search_result()
                  .with_title("My Article")
                  .with_url("https://example.com")
                  .with_snippet("A great article about...")
                  .build())
    """

    def __init__(self):
        self._title = "Default Test Article"
        self._url = "https://example.com/test"
        self._snippet = "This is a test search result snippet."
        self._content = ""

    def with_title(self, title: str) -> "SearchResultBuilder":
        """Set the title."""
        self._title = title
        return self

    def with_url(self, url: str) -> "SearchResultBuilder":
        """Set the URL."""
        self._url = url
        return self

    def with_snippet(self, snippet: str) -> "SearchResultBuilder":
        """Set the snippet."""
        self._snippet = snippet
        return self

    def with_content(self, content: str) -> "SearchResultBuilder":
        """Set the content."""
        self._content = content
        return self

    def with_markdown_content(self) -> "SearchResultBuilder":
        """Pre-fill with markdown content for testing."""
        self._content = (
            f"# {self._title}\n\n*Source: {self._url}*\n\nTest markdown content."
        )
        return self

    def build(self) -> SearchResult:
        """Build the SearchResult instance."""
        return SearchResult(
            title=self._title,
            url=self._url,
            snippet=self._snippet,
            content=self._content,
        )


def a_search_result() -> SearchResultBuilder:
    """Entry point for creating SearchResult builders."""
    return SearchResultBuilder()


def a_wikipedia_article() -> SearchResultBuilder:
    """Pre-configured builder for Wikipedia articles."""
    return (
        SearchResultBuilder()
        .with_title("Python (programming language) - Wikipedia")
        .with_url("https://en.wikipedia.org/wiki/Python_(programming_language)")
        .with_snippet("Python is a high-level programming language...")
    )
