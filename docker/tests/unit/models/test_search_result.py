# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for SearchResult model."""

from models.search_result import SearchResult


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_creates_with_required_fields(self):
        # Act
        result = SearchResult(title="Test", url="https://test.com", snippet="Snippet")

        # Assert
        assert result.title == "Test"
        assert result.url == "https://test.com"
        assert result.snippet == "Snippet"
        assert result.content == ""

    def test_accepts_optional_content(self):
        # Act
        result = SearchResult(
            title="Test", url="https://test.com", snippet="S", content="Content"
        )

        # Assert
        assert result.content == "Content"
