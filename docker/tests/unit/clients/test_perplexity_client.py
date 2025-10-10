# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for Perplexity API client."""

from unittest.mock import patch

import pytest

from clients.perplexity_client import fetch_perplexity_deep_research
from tests.factories.perplexity_response_factory import PerplexityResponseFactory


@pytest.mark.unit
@patch("clients.perplexity_client.Perplexity")
def test_fetch_perplexity_deep_research_success(mock_perplexity_class):
    """Test successful deep research fetch."""
    # Setup using factory
    response = PerplexityResponseFactory.successful_research()
    mock_client = PerplexityResponseFactory.client_with_response(response)
    mock_perplexity_class.return_value = mock_client

    # Call function
    report, citations = fetch_perplexity_deep_research(
        query="What is Python?",
        api_key="test_key",  # pragma: allowlist secret
        max_results=3,
        research_effort="low",
    )

    # Assertions
    assert report == "Python is a high-level programming language."
    assert len(citations) == 2
    assert citations[0] == "https://python.org"

    # Verify client was initialized with correct timeout
    mock_perplexity_class.assert_called_once_with(
        api_key="test_key", timeout=600.0  # pragma: allowlist secret
    )


@pytest.mark.unit
@patch("clients.perplexity_client.Perplexity")
def test_fetch_perplexity_deep_research_empty_response(mock_perplexity_class):
    """Test handling of empty response."""
    # Setup using factory
    response = PerplexityResponseFactory.empty_response()
    mock_client = PerplexityResponseFactory.client_with_response(response)
    mock_perplexity_class.return_value = mock_client

    # Call function
    report, citations = fetch_perplexity_deep_research(
        query="What is Python?",
        api_key="test_key",  # pragma: allowlist secret
    )

    # Assertions
    assert report == ""
    assert citations == []


@pytest.mark.unit
@patch("clients.perplexity_client.Perplexity")
def test_fetch_perplexity_deep_research_api_error(mock_perplexity_class):
    """Test handling of API errors."""
    # Setup using factory - client raises exception
    mock_client = PerplexityResponseFactory.client_with_response(
        PerplexityResponseFactory.empty_response()
    )
    mock_client.chat.completions.create = lambda **kwargs: (_ for _ in ()).throw(
        PerplexityResponseFactory.api_error()
    )
    mock_perplexity_class.return_value = mock_client

    # Call function
    report, citations = fetch_perplexity_deep_research(
        query="What is Python?",
        api_key="test_key",  # pragma: allowlist secret
    )

    # Assertions - should return empty values on error
    assert report == ""
    assert citations == []


@pytest.mark.unit
@patch("clients.perplexity_client.Perplexity")
def test_fetch_perplexity_deep_research_max_results_limit(mock_perplexity_class):
    """Test that max_results limits citations returned."""
    # Setup using factory with many citations
    response = PerplexityResponseFactory.with_many_citations(num_citations=5)
    mock_client = PerplexityResponseFactory.client_with_response(response)
    mock_perplexity_class.return_value = mock_client

    # Call function with max_results=2
    report, citations = fetch_perplexity_deep_research(
        query="Test query",
        api_key="test_key",  # pragma: allowlist secret
        max_results=2,
    )

    # Assertions - should only return 2 citations
    assert len(citations) == 2
    assert citations == ["https://url1.com", "https://url2.com"]


@pytest.mark.unit
@patch("clients.perplexity_client.Perplexity")
def test_fetch_perplexity_deep_research_no_citations(mock_perplexity_class):
    """Test handling when API returns no citations."""
    # Setup using factory without citations
    response = PerplexityResponseFactory.without_citations()
    mock_client = PerplexityResponseFactory.client_with_response(response)
    mock_perplexity_class.return_value = mock_client

    # Call function
    report, citations = fetch_perplexity_deep_research(
        query="Test query",
        api_key="test_key",  # pragma: allowlist secret
    )

    # Assertions
    assert report == "Research without citations"
    assert citations == []
