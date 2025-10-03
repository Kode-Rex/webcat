# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for content scraper service."""

import pytest
from unittest.mock import patch

from constants import MAX_CONTENT_LENGTH
from services.content_scraper import scrape_search_result
from tests.builders.search_result_builder import a_search_result
from tests.factories.http_response_factory import HttpResponseFactory


class TestContentScraperSuccess:
    """Tests for successful content scraping scenarios."""

    @patch("services.content_scraper.requests.get")
    def test_converts_html_to_markdown_with_title(self, mock_get):
        # Arrange
        result = a_search_result().with_title("Test Article").build()
        mock_get.return_value = HttpResponseFactory.html_with_title("Test Article")

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert scraped.content.startswith("# Test Article")
        assert "*Source: https://example.com/test*" in scraped.content

    @patch("services.content_scraper.requests.get")
    def test_wraps_plaintext_in_code_blocks(self, mock_get):
        # Arrange
        result = a_search_result().build()
        mock_get.return_value = HttpResponseFactory.plaintext("Plain text content")

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "```" in scraped.content
        assert "Plain text content" in scraped.content

    @patch("services.content_scraper.requests.get")
    def test_handles_pdf_files_with_message(self, mock_get):
        # Arrange
        result = a_search_result().build()
        mock_get.return_value = HttpResponseFactory.pdf()

        # Act
        scraped = scrape_search_result(result)

        # Assert
        assert "binary file" in scraped.content
        assert "application/pdf" in scraped.content


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


class TestContentScraperEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @patch("services.content_scraper.requests.get")
    def test_truncates_content_exceeding_max_length(self, mock_get):
        # Arrange
        large_content = "<html><body>" + ("x" * 100000) + "</body></html>"
        result = a_search_result().build()
        mock_get.return_value = HttpResponseFactory.success(content=large_content)

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
