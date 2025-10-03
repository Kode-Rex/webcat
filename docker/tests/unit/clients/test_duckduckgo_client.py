# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for DuckDuckGo client."""

from unittest.mock import MagicMock, patch

from clients.duckduckgo_client import fetch_duckduckgo_search_results


class TestDuckDuckGoClientWithLibrary:
    """Tests when duckduckgo-search library is available."""

    @patch("clients.duckduckgo_client.DDGS")
    def test_returns_search_results(self, mock_ddgs_class):
        # Arrange
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "href": "https://ex.com/1", "body": "Body 1"},
            {"title": "Result 2", "href": "https://ex.com/2", "body": "Body 2"},
        ]

        # Act
        results = fetch_duckduckgo_search_results("test query", max_results=2)

        # Assert
        assert len(results) == 2
        assert results[0].title == "Result 1"
        assert results[0].link == "https://ex.com/1"
        assert results[0].snippet == "Body 1"

    @patch("clients.duckduckgo_client.DDGS")
    def test_respects_max_results(self, mock_ddgs_class):
        # Arrange
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = []

        # Act
        fetch_duckduckgo_search_results("test query", max_results=5)

        # Assert
        mock_ddgs.text.assert_called_once_with("test query", max_results=5)

    @patch("clients.duckduckgo_client.DDGS")
    def test_handles_exception(self, mock_ddgs_class):
        # Arrange
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.side_effect = Exception("API error")

        # Act
        results = fetch_duckduckgo_search_results("test query")

        # Assert
        assert len(results) == 0

    @patch("clients.duckduckgo_client.DDGS")
    def test_handles_missing_fields_with_defaults(self, mock_ddgs_class):
        # Arrange
        mock_ddgs = MagicMock()
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [{}]  # Missing all fields

        # Act
        results = fetch_duckduckgo_search_results("test query")

        # Assert
        assert len(results) == 1
        assert results[0].title == "Untitled"
        assert results[0].link == ""
        assert results[0].snippet == ""


class TestDuckDuckGoClientWithoutLibrary:
    """Tests when duckduckgo-search library is not available."""

    @patch("clients.duckduckgo_client.DDGS", None)
    def test_returns_empty_when_library_missing(self):
        # Act
        results = fetch_duckduckgo_search_results("test query")

        # Assert
        assert len(results) == 0
