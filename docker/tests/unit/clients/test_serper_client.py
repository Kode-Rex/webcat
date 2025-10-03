# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for Serper client."""

from unittest.mock import patch

from clients.serper_client import fetch_search_results
from tests.factories.serper_response_factory import SerperResponseFactory


class TestSerperClient:
    """Tests for Serper API client."""

    @patch("clients.serper_client.requests.post")
    def test_returns_search_results_from_organic(self, mock_post):
        # Arrange
        mock_post.return_value = SerperResponseFactory.two_results()

        # Act
        results = fetch_search_results("test query", "fake_api_key")

        # Assert
        assert len(results) == 2
        assert results[0].title == "Result 1"
        assert results[0].link == "https://example.com/1"
        assert results[1].title == "Result 2"

    @patch("clients.serper_client.requests.post")
    def test_returns_empty_when_no_organic_results(self, mock_post):
        # Arrange
        mock_post.return_value = SerperResponseFactory.empty()

        # Act
        results = fetch_search_results("test query", "fake_api_key")

        # Assert
        assert len(results) == 0

    @patch("clients.serper_client.requests.post")
    def test_handles_request_exception(self, mock_post):
        # Arrange
        mock_post.side_effect = Exception("Network error")

        # Act
        results = fetch_search_results("test query", "fake_api_key")

        # Assert
        assert len(results) == 0

    @patch("clients.serper_client.requests.post")
    def test_uses_correct_api_endpoint(self, mock_post):
        # Arrange
        mock_post.return_value = SerperResponseFactory.empty()

        # Act
        fetch_search_results("test query", "fake_api_key")

        # Assert
        assert mock_post.call_args[0][0] == "https://google.serper.dev/search"

    @patch("clients.serper_client.requests.post")
    def test_handles_missing_fields_with_defaults(self, mock_post):
        # Arrange
        mock_post.return_value = SerperResponseFactory.with_results([{}])

        # Act
        results = fetch_search_results("test query", "fake_api_key")

        # Assert
        assert len(results) == 1
        assert results[0].title == "Untitled"
        assert results[0].link == ""
        assert results[0].snippet == ""
