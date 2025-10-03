# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for health check tool."""

import pytest

from tools.health_check_tool import health_check_tool


class TestHealthCheckTool:
    """Tests for health check tool."""

    @pytest.mark.asyncio
    async def test_returns_healthy_status(self):
        # Act
        result = await health_check_tool()

        # Assert
        assert result["status"] == "healthy"
        assert result["service"] == "webcat"

    @pytest.mark.asyncio
    async def test_returns_dict(self):
        # Act
        result = await health_check_tool()

        # Assert
        assert isinstance(result, dict)
        assert "status" in result
        assert "service" in result
