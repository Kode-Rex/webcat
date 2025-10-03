# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for DuckDuckGo client when library is not available."""

from unittest.mock import patch

from clients.duckduckgo_client import fetch_duckduckgo_search_results


class TestDuckDuckGoClientWithoutLibrary:
    """Tests when duckduckgo-search library is not available."""

    @patch("clients.duckduckgo_client.DDGS", None)
    def test_returns_empty_when_library_missing(self):
        # Act
        results = fetch_duckduckgo_search_results("test query")

        # Assert
        assert len(results) == 0
