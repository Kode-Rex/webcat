# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health responses module.

DEPRECATED: Import from models.responses.health_responses instead.
"""

import warnings

from models.responses.health_responses import (
    get_detailed_status,
    get_health_status,
    get_root_info,
    get_server_configuration,
    get_server_endpoints,
    get_status_error,
    get_unhealthy_status,
)

warnings.warn(
    "Importing from 'models.health_responses' is deprecated. Use 'models.responses.health_responses' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "get_health_status",
    "get_unhealthy_status",
    "get_server_configuration",
    "get_server_endpoints",
    "get_detailed_status",
    "get_status_error",
    "get_root_info",
]
