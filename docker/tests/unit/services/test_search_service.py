# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for search service."""

from unittest.mock import patch

from models.api_search_result import APISearchResult
from services.search_service import fetch_with_fallback


class TestSearchServiceWithSerperKey:
    """Tests for search with Serper API key configured."""

    @patch("services.search_service.fetch_search_results")
    def test_uses_serper_when_key_provided(self, mock_serper):
        # Arrange
        mock_serper.return_value = [
            APISearchResult(title="Test", link="https://test.com", snippet="Snippet")
        ]

        # Act
        results, source = fetch_with_fallback("test query", serper_api_key="fake_key")

        # Assert
        assert source == "Serper API"
        assert len(results) == 1
        assert results[0].title == "Test"
        mock_serper.assert_called_once_with("test query", "fake_key")

    @patch("services.search_service.fetch_duckduckgo_search_results")
    @patch("services.search_service.fetch_search_results")
    def test_falls_back_to_ddg_when_serper_returns_empty(self, mock_serper, mock_ddg):
        # Arrange
        mock_serper.return_value = []
        mock_ddg.return_value = [
            APISearchResult(title="DDG", link="https://ddg.com", snippet="DDG result")
        ]

        # Act
        results, source = fetch_with_fallback("test query", serper_api_key="fake_key")

        # Assert
        assert source == "DuckDuckGo (free fallback)"
        assert len(results) == 1
        assert results[0].title == "DDG"


class TestSearchServiceWithoutSerperKey:
    """Tests for search without Serper API key."""

    @patch("services.search_service.fetch_duckduckgo_search_results")
    def test_uses_duckduckgo_when_no_key(self, mock_ddg):
        # Arrange
        mock_ddg.return_value = [
            APISearchResult(title="DDG", link="https://ddg.com", snippet="DDG result")
        ]

        # Act
        results, source = fetch_with_fallback("test query", serper_api_key="")

        # Assert
        assert source == "DuckDuckGo (free fallback)"
        assert len(results) == 1

    @patch("services.search_service.fetch_duckduckgo_search_results")
    def test_returns_empty_when_ddg_fails(self, mock_ddg):
        # Arrange
        mock_ddg.return_value = []

        # Act
        results, source = fetch_with_fallback("test query", serper_api_key="")

        # Assert
        assert source == "DuckDuckGo (free fallback)"
        assert len(results) == 0
