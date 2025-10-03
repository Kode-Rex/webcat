# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for APISearchResult model."""

from models.api_search_result import APISearchResult


class TestAPISearchResult:
    """Tests for APISearchResult model."""

    def test_creates_with_required_fields(self):
        # Act
        result = APISearchResult(title="Test", link="https://test.com", snippet="S")

        # Assert
        assert result.title == "Test"
        assert result.link == "https://test.com"
        assert result.snippet == "S"
