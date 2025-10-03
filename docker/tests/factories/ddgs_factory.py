# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Factory for creating DuckDuckGo Search test doubles."""

from typing import Any, Dict, List

from tests.factories.mock_ddgs import MockDDGS, MockDDGSClass


class DDGSFactory:
    """Factory for creating pre-configured DDGS mocks."""

    @staticmethod
    def with_results(results: List[Dict[str, Any]]) -> MockDDGSClass:
        """Create DDGS that returns specific results.

        Args:
            results: List of result dictionaries with title, href, body

        Returns:
            MockDDGSClass that returns these results
        """
        ddgs = MockDDGS(results=results)
        return MockDDGSClass(ddgs)

    @staticmethod
    def empty() -> MockDDGSClass:
        """Create DDGS that returns no results.

        Returns:
            MockDDGSClass that returns empty list
        """
        ddgs = MockDDGS(results=[])
        return MockDDGSClass(ddgs)

    @staticmethod
    def two_results() -> MockDDGSClass:
        """Create DDGS with two example results.

        Returns:
            MockDDGSClass with two pre-configured results
        """
        ddgs = MockDDGS(
            results=[
                {"title": "Result 1", "href": "https://ex.com/1", "body": "Body 1"},
                {"title": "Result 2", "href": "https://ex.com/2", "body": "Body 2"},
            ]
        )
        return MockDDGSClass(ddgs)

    @staticmethod
    def with_exception(exception: Exception) -> MockDDGSClass:
        """Create DDGS that raises an exception.

        Args:
            exception: Exception to raise

        Returns:
            MockDDGSClass that raises exception when text() is called
        """
        ddgs = MockDDGS(should_raise=exception)
        return MockDDGSClass(ddgs)

    @staticmethod
    def with_missing_fields() -> MockDDGSClass:
        """Create DDGS with results missing optional fields.

        Returns:
            MockDDGSClass with incomplete result data
        """
        ddgs = MockDDGS(
            results=[
                {
                    "title": "Title Only",
                    # Missing href and body
                }
            ]
        )
        return MockDDGSClass(ddgs)
