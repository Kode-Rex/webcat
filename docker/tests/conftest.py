# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Shared pytest fixtures and configuration for all tests."""

import logging
import os
import tempfile

import pytest

from tests.builders.search_result_builder import a_search_result, a_wikipedia_article
from tests.factories.http_response_factory import HttpResponseFactory


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    """
    Configure environment for all tests.

    Runs once at the start of the test session.
    """
    # Set up test environment variables
    os.environ["LOG_DIR"] = tempfile.gettempdir()
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ.pop("SERPER_API_KEY", None)  # Ensure no real API key in tests

    # Configure logging to reduce noise
    logging.basicConfig(
        level=logging.WARNING, format="%(levelname)s - %(name)s - %(message)s"
    )

    yield

    # Cleanup after all tests (if needed)
    pass


@pytest.fixture
def search_result_builder():
    """Provide a SearchResult builder for tests."""
    return a_search_result()


@pytest.fixture
def wikipedia_result():
    """Provide a pre-configured Wikipedia search result."""
    return a_wikipedia_article().build()


@pytest.fixture
def http_factory():
    """Provide HTTP response factory for mocking."""
    return HttpResponseFactory()


@pytest.fixture
def mock_successful_http_get(monkeypatch, http_factory):
    """
    Automatically mock requests.get to return successful HTML response.

    Use this for tests that don't care about specific HTTP behavior.
    """

    def mock_get(*args, **kwargs):
        return http_factory.success()

    monkeypatch.setattr("requests.get", mock_get)
    return mock_get


@pytest.fixture
def temp_test_dir(tmp_path):
    """Provide a temporary directory for tests that need file I/O."""
    test_dir = tmp_path / "webcat_test"
    test_dir.mkdir()
    return test_dir
