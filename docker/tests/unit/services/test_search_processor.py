# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for search processor service."""

from unittest.mock import patch

from models.search_result import SearchResult
from services.search_processor import process_search_results
from tests.builders.api_search_result_builder import an_api_search_result


class TestSearchProcessor:
    """Tests for search result processing."""

    @patch("services.search_processor.scrape_search_result")
    def test_processes_single_result(self, mock_scrape):
        # Arrange
        api_result = (
            an_api_search_result()
            .with_title("Test")
            .with_link("https://test.com")
            .with_snippet("Snippet")
            .build()
        )
        scraped = SearchResult(
            title="Test", url="https://test.com", snippet="Snippet", content="Content"
        )
        mock_scrape.return_value = scraped

        # Act
        results = process_search_results([api_result])

        # Assert
        assert len(results) == 1
        assert results[0].title == "Test"
        assert results[0].content == "Content"

    @patch("services.search_processor.scrape_search_result")
    def test_processes_multiple_results(self, mock_scrape):
        # Arrange
        api_results = [
            an_api_search_result()
            .with_title("Test1")
            .with_link("https://test1.com")
            .with_snippet("S1")
            .build(),
            an_api_search_result()
            .with_title("Test2")
            .with_link("https://test2.com")
            .with_snippet("S2")
            .build(),
        ]
        mock_scrape.side_effect = [
            SearchResult(
                title="Test1", url="https://test1.com", snippet="S1", content="C1"
            ),
            SearchResult(
                title="Test2", url="https://test2.com", snippet="S2", content="C2"
            ),
        ]

        # Act
        results = process_search_results(api_results)

        # Assert
        assert len(results) == 2
        assert results[0].title == "Test1"
        assert results[1].title == "Test2"

    @patch("services.search_processor.scrape_search_result")
    def test_handles_empty_list(self, mock_scrape):
        # Arrange - Act
        results = process_search_results([])

        # Assert
        assert len(results) == 0
        mock_scrape.assert_not_called()

    @patch("services.search_processor.scrape_search_result")
    def test_converts_api_result_fields_correctly(self, mock_scrape):
        # Arrange
        api_result = (
            an_api_search_result()
            .with_title("Original")
            .with_link("https://orig.com")
            .with_snippet("Original snippet")
            .build()
        )
        mock_scrape.return_value = SearchResult(
            title="Original",
            url="https://orig.com",
            snippet="Original snippet",
            content="Scraped",
        )

        # Act
        process_search_results([api_result])

        # Assert
        call_args = mock_scrape.call_args[0][0]
        assert call_args.title == "Original"
        assert call_args.url == "https://orig.com"
        assert call_args.snippet == "Original snippet"
