# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for edge cases and boundary conditions."""

from unittest.mock import patch

from constants import MAX_CONTENT_LENGTH
from services.content_scraper import scrape_search_result
from tests.builders.search_result_builder import a_search_result
from tests.factories.http_response_factory import HttpResponseFactory


class TestContentScraperEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @patch("services.content_scraper.trafilatura.extract")
    @patch("services.content_scraper.requests.get")
    def test_truncates_content_exceeding_max_length(self, mock_get, mock_trafilatura):
        # Arrange
        large_content = "<html><body>" + ("x" * 100000) + "</body></html>"
        result = a_search_result().build()
        mock_get.return_value = HttpResponseFactory.success(content=large_content)

        # Mock trafilatura to return large content
        mock_trafilatura.return_value = "x" * 100000

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "[content truncated]" in scraped.content
        assert len(scraped.content) <= MAX_CONTENT_LENGTH + 100  # Some buffer

    @patch("services.content_scraper.requests.get")
    def test_handles_connection_error(self, mock_get):
        # Arrange
        result = a_search_result().build()
        mock_get.side_effect = HttpResponseFactory.connection_error()

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "Error: Failed to retrieve" in scraped.content

    @patch("services.content_scraper.requests.get")
    def test_handles_readability_failure_with_fallback(self, mock_get):
        # Arrange - malformed HTML that readability might reject
        bad_html = "<html><body><<<<>>>>>nonsense</body></html>"
        result = a_search_result().build()
        mock_get.return_value = HttpResponseFactory.success(content=bad_html)

        # Act
        scraped = scrape_search_result(result)

        # Assert
        # Should still produce some content via fallback
        assert scraped.content != ""
