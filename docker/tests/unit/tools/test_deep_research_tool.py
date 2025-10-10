# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for deep_research_tool."""

from unittest.mock import patch

import pytest

from tools.deep_research_tool import deep_research_tool


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "test_key")
@patch("tools.deep_research_tool.fetch_perplexity_deep_research")
async def test_deep_research_tool_success(mock_fetch):
    """Test successful deep research."""
    # Setup mock
    mock_fetch.return_value = (
        "Python is a high-level programming language.",
        ["https://python.org", "https://docs.python.org"],
    )

    # Call tool
    result = await deep_research_tool(
        query="What is Python?",
        research_effort="low",
        max_results=2,
    )

    # Assertions
    assert result["query"] == "What is Python?"
    assert result["search_source"] == "Perplexity Deep Research (effort: low)"
    assert len(result["results"]) == 1

    # Check content includes report and citations
    content = result["results"][0]["content"]
    assert "# Deep Research: What is Python?" in content
    assert "*Research Effort: Low*" in content
    assert "Python is a high-level programming language." in content
    assert "## Sources" in content
    assert "1. https://python.org" in content
    assert "2. https://docs.python.org" in content


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "")
async def test_deep_research_tool_no_api_key():
    """Test deep research when API key is not configured."""
    # Call tool without API key
    result = await deep_research_tool(query="What is Python?")

    # Assertions
    assert result["query"] == "What is Python?"
    assert "not configured" in result["search_source"]
    assert result["results"] == []
    assert "PERPLEXITY_API_KEY" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "test_key")
@patch("tools.deep_research_tool.fetch_perplexity_deep_research")
async def test_deep_research_tool_empty_response(mock_fetch):
    """Test deep research when API returns empty response."""
    # Setup mock to return empty
    mock_fetch.return_value = ("", [])

    # Call tool
    result = await deep_research_tool(query="What is Python?")

    # Assertions
    assert result["query"] == "What is Python?"
    assert result["results"] == []
    assert "failed" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "test_key")
@patch("tools.deep_research_tool.fetch_perplexity_deep_research")
async def test_deep_research_tool_default_params(mock_fetch):
    """Test deep research with default parameters."""
    # Setup mock
    mock_fetch.return_value = ("Research report", ["https://example.com"])

    # Call tool with only required param
    result = await deep_research_tool(query="Test query")

    # Verify defaults were used
    mock_fetch.assert_called_once_with(
        query="Test query",
        api_key="test_key",  # pragma: allowlist secret
        max_results=5,  # default
        research_effort="high",  # default
    )

    # Check result
    assert result["search_source"] == "Perplexity Deep Research (effort: high)"


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "test_key")
@patch("tools.deep_research_tool.fetch_perplexity_deep_research")
async def test_deep_research_tool_custom_effort_levels(mock_fetch):
    """Test deep research with different effort levels."""
    mock_fetch.return_value = ("Report", [])

    # Test low effort
    result = await deep_research_tool(query="Test", research_effort="low")
    assert "*Research Effort: Low*" in result["results"][0]["content"]

    # Test medium effort
    result = await deep_research_tool(query="Test", research_effort="medium")
    assert "*Research Effort: Medium*" in result["results"][0]["content"]

    # Test high effort
    result = await deep_research_tool(query="Test", research_effort="high")
    assert "*Research Effort: High*" in result["results"][0]["content"]


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "test_key")
@patch("tools.deep_research_tool.fetch_perplexity_deep_research")
async def test_deep_research_tool_no_citations(mock_fetch):
    """Test deep research when no citations are returned."""
    # Setup mock with no citations
    mock_fetch.return_value = ("Research content without citations", [])

    # Call tool
    result = await deep_research_tool(query="Test query")

    # Assertions
    content = result["results"][0]["content"]
    assert "Research content without citations" in content
    assert "## Sources" not in content  # Sources section should not be added


@pytest.mark.unit
@pytest.mark.asyncio
@patch("tools.deep_research_tool.PERPLEXITY_API_KEY", "test_key")
@patch("tools.deep_research_tool.fetch_perplexity_deep_research")
async def test_deep_research_tool_long_report_snippet(mock_fetch):
    """Test that snippet is truncated for long reports."""
    # Setup mock with very long report
    long_report = "A" * 1000
    mock_fetch.return_value = (long_report, [])

    # Call tool
    result = await deep_research_tool(query="Test")

    # Check snippet is truncated to 500 chars + "..."
    snippet = result["results"][0]["snippet"]
    assert len(snippet) == 503  # 500 + "..."
    assert snippet.endswith("...")
