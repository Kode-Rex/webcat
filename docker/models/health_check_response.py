# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""HealthCheckResponse model - response from health check tool."""

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Response from health check tool."""

    status: str
    service: str
