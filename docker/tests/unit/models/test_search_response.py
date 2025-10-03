# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for SearchResponse model."""

from models.search_response import SearchResponse
from models.search_result import SearchResult


class TestSearchResponse:
    """Tests for SearchResponse model."""

    def test_creates_with_required_fields(self):
        # Arrange
        results = [SearchResult(title="T", url="U", snippet="S")]

        # Act
        response = SearchResponse(query="test", search_source="Serper", results=results)

        # Assert
        assert response.query == "test"
        assert response.search_source == "Serper"
        assert len(response.results) == 1
        assert response.error is None
