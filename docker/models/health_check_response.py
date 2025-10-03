# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health check response model.

DEPRECATED: Import from models.responses.health_check_response instead.
"""

import warnings

from models.responses.health_check_response import HealthCheckResponse

warnings.warn(
    "Importing from 'models.health_check_response' is deprecated. Use 'models.responses.health_check_response' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["HealthCheckResponse"]
