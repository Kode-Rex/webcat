# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for search service without Serper API key."""

from unittest.mock import patch

from services.search_service import fetch_with_fallback
from tests.builders.api_search_result_builder import a_duckduckgo_result


class TestSearchServiceWithoutSerperKey:
    """Tests for search without Serper API key."""

    @patch("services.search_service.fetch_duckduckgo_search_results")
    def test_uses_duckduckgo_when_no_key(self, mock_ddg):
        # Arrange
        mock_ddg.return_value = [a_duckduckgo_result().build()]

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
