# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for HealthCheckResponse model."""

from models.health_check_response import HealthCheckResponse


class TestHealthCheckResponse:
    """Tests for HealthCheckResponse model."""

    def test_creates_with_required_fields(self):
        # Act
        response = HealthCheckResponse(status="healthy", service="webcat")

        # Assert
        assert response.status == "healthy"
        assert response.service == "webcat"
