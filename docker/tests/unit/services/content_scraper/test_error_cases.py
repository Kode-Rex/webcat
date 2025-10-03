# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for error handling in content scraping."""

from unittest.mock import patch

from services.content_scraper import scrape_search_result
from tests.builders.search_result_builder import a_search_result
from tests.factories.http_response_factory import HttpResponseFactory


class TestContentScraperErrors:
    """Tests for error handling in content scraping."""

    @patch("services.content_scraper.requests.get")
    def test_returns_error_message_on_404(self, mock_get):
        # Arrange
        result = a_search_result().build()
        mock_get.return_value = HttpResponseFactory.error_404()

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "Error: Failed to retrieve" in scraped.content

    @patch("services.content_scraper.requests.get")
    def test_returns_error_message_on_timeout(self, mock_get):
        # Arrange
        result = a_search_result().build()
        mock_get.side_effect = HttpResponseFactory.timeout()

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "Error: Failed to retrieve" in scraped.content
        assert "timed out" in scraped.content.lower()

    def test_returns_error_when_url_missing(self):
        # Arrange
        result = a_search_result().with_url("").build()

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "Error: Missing URL" in scraped.content
