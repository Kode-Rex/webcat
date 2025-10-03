# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for Serper client."""

from unittest.mock import MagicMock, patch

from clients.serper_client import fetch_search_results


class TestSerperClient:
    """Tests for Serper API client."""

    @patch("clients.serper_client.requests.post")
    def test_returns_search_results_from_organic(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": "Result 1",
                    "link": "https://example.com/1",
                    "snippet": "Snippet 1",
                },
                {
                    "title": "Result 2",
                    "link": "https://example.com/2",
                    "snippet": "Snippet 2",
                },
            ]
        }
        mock_post.return_value = mock_response

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
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

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
        mock_response = MagicMock()
        mock_response.json.return_value = {"organic": []}
        mock_post.return_value = mock_response

        # Act
        fetch_search_results("test query", "fake_api_key")

        # Assert
        assert mock_post.call_args[0][0] == "https://google.serper.dev/search"

    @patch("clients.serper_client.requests.post")
    def test_handles_missing_fields_with_defaults(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "organic": [
                {},  # Missing all fields
            ]
        }
        mock_post.return_value = mock_response

        # Act
        results = fetch_search_results("test query", "fake_api_key")

        # Assert
        assert len(results) == 1
        assert results[0].title == "Untitled"
        assert results[0].link == ""
        assert results[0].snippet == ""
