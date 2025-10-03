# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Mock context manager for DDGS."""

from tests.factories.mock_ddgs_search_client import MockDDGS


class MockDDGSContextManager:
    """Mock context manager for DDGS."""

    def __init__(self, ddgs_instance: MockDDGS):
        """Initialize with DDGS instance."""
        self._ddgs = ddgs_instance

    def __enter__(self) -> MockDDGS:
        """Enter context manager."""
        return self._ddgs

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass
