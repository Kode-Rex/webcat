# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""API responses module.

DEPRECATED: Import from models.responses.api_responses instead.
"""

import warnings

from models.responses.api_responses import (
    APIHealthCheckResponse,
    APIScrapeResponse,
    APISearchToolResponse,
    APIServerInfoResponse,
)

warnings.warn(
    "Importing from 'models.api_responses' is deprecated. Use 'models.responses.api_responses' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "APISearchToolResponse",
    "APIHealthCheckResponse",
    "APIServerInfoResponse",
    "APIScrapeResponse",
]
