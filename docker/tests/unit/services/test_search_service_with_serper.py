# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for search service with Serper API key configured."""

from unittest.mock import patch

from services.search_service import fetch_with_fallback
from tests.builders.api_search_result_builder import (
    a_duckduckgo_result,
    a_serper_result,
)


class TestSearchServiceWithSerperKey:
    """Tests for search with Serper API key configured."""

    @patch("services.search_service.fetch_search_results")
    def test_uses_serper_when_key_provided(self, mock_serper):
        # Arrange
        mock_serper.return_value = [a_serper_result().build()]

        # Act
        results, source = fetch_with_fallback("test query", serper_api_key="fake_key")

        # Assert
        assert source == "Serper API"
        assert len(results) == 1
        assert results[0].title == "Serper Result"
        mock_serper.assert_called_once_with("test query", "fake_key")

    @patch("services.search_service.fetch_duckduckgo_search_results")
    @patch("services.search_service.fetch_search_results")
    def test_falls_back_to_ddg_when_serper_returns_empty(self, mock_serper, mock_ddg):
        # Arrange
        mock_serper.return_value = []
        mock_ddg.return_value = [a_duckduckgo_result().build()]

        # Act
        results, source = fetch_with_fallback("test query", serper_api_key="fake_key")

        # Assert
        assert source == "DuckDuckGo (free fallback)"
        assert len(results) == 1
        assert results[0].title == "DuckDuckGo Result"
