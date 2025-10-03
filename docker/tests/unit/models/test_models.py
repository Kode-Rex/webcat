# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for Pydantic models."""

import pytest

from models.api_search_result import APISearchResult
from models.error_response import ErrorResponse
from models.health_check_response import HealthCheckResponse
from models.search_response import SearchResponse
from models.search_result import SearchResult


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_creates_with_required_fields(self):
        # Act
        result = SearchResult(title="Test", url="https://test.com", snippet="Snippet")

        # Assert
        assert result.title == "Test"
        assert result.url == "https://test.com"
        assert result.snippet == "Snippet"
        assert result.content == ""

    def test_accepts_optional_content(self):
        # Act
        result = SearchResult(
            title="Test", url="https://test.com", snippet="S", content="Content"
        )

        # Assert
        assert result.content == "Content"


class TestAPISearchResult:
    """Tests for APISearchResult model."""

    def test_creates_with_required_fields(self):
        # Act
        result = APISearchResult(title="Test", link="https://test.com", snippet="S")

        # Assert
        assert result.title == "Test"
        assert result.link == "https://test.com"
        assert result.snippet == "S"


class TestSearchResponse:
    """Tests for SearchResponse model."""

    def test_creates_with_required_fields(self):
        # Arrange
        results = [SearchResult(title="T", url="U", snippet="S")]

        # Act
        response = SearchResponse(
            query="test", search_source="Serper", results=results
        )

        # Assert
        assert response.query == "test"
        assert response.search_source == "Serper"
        assert len(response.results) == 1
        assert response.error is None


class TestHealthCheckResponse:
    """Tests for HealthCheckResponse model."""

    def test_creates_with_required_fields(self):
        # Act
        response = HealthCheckResponse(status="healthy", service="webcat")

        # Assert
        assert response.status == "healthy"
        assert response.service == "webcat"


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_creates_with_error(self):
        # Act
        response = ErrorResponse(error="Something went wrong")

        # Assert
        assert response.error == "Something went wrong"
        assert response.query is None
        assert response.details is None

    def test_accepts_optional_fields(self):
        # Act
        response = ErrorResponse(
            error="Error", query="test query", details="More info"
        )

        # Assert
        assert response.query == "test query"
        assert response.details == "More info"
