# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for ErrorResponse model."""

from models.error_response import ErrorResponse


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
        response = ErrorResponse(error="Error", query="test query", details="More info")

        # Assert
        assert response.query == "test query"
        assert response.details == "More info"
