# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for search tool."""

from unittest.mock import patch

import pytest

from models.api_search_result import APISearchResult
from models.search_result import SearchResult
from tools.search_tool import search_tool


class TestSearchTool:
    """Tests for search tool."""

    @pytest.mark.asyncio
    @patch("tools.search_tool.process_search_results")
    @patch("tools.search_tool.fetch_with_fallback")
    async def test_returns_search_results(self, mock_fetch, mock_process):
        # Arrange
        api_results = [
            APISearchResult(title="Test", link="https://test.com", snippet="Snippet")
        ]
        processed = [
            SearchResult(
                title="Test",
                url="https://test.com",
                snippet="Snippet",
                content="Content",
            )
        ]
        mock_fetch.return_value = (api_results, "Serper API")
        mock_process.return_value = processed

        # Act
        result = await search_tool("test query")

        # Assert
        assert result["query"] == "test query"
        assert result["search_source"] == "Serper API"
        assert len(result["results"]) == 1
        assert result["results"][0]["title"] == "Test"

    @pytest.mark.asyncio
    @patch("tools.search_tool.fetch_with_fallback")
    async def test_returns_error_when_no_results(self, mock_fetch):
        # Arrange
        mock_fetch.return_value = ([], "DuckDuckGo (free fallback)")

        # Act
        result = await search_tool("test query")

        # Assert
        assert result["query"] == "test query"
        assert result["error"] == "No search results found from any source."
        assert len(result["results"]) == 0

    @pytest.mark.asyncio
    @patch("tools.search_tool.process_search_results")
    @patch("tools.search_tool.fetch_with_fallback")
    async def test_processes_results_correctly(self, mock_fetch, mock_process):
        # Arrange
        api_results = [APISearchResult(title="T", link="L", snippet="S")]
        mock_fetch.return_value = (api_results, "Source")
        mock_process.return_value = []

        # Act
        await search_tool("query")

        # Assert
        mock_process.assert_called_once_with(api_results)
