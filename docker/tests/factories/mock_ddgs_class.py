# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Mock DDGS class that returns context manager."""

from tests.factories.mock_ddgs_context_manager import MockDDGSContextManager
from tests.factories.mock_ddgs_search_client import MockDDGS


class MockDDGSClass:
    """Mock DDGS class that returns context manager."""

    def __init__(self, ddgs_instance: MockDDGS):
        """Initialize with DDGS instance."""
        self._ddgs = ddgs_instance

    def __call__(self, *args, **kwargs) -> MockDDGSContextManager:
        """Return context manager when instantiated."""
        return MockDDGSContextManager(self._ddgs)
