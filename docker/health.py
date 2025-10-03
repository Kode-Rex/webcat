# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Health endpoints module for WebCat MCP server.

DEPRECATED: Import from endpoints.health_endpoints and endpoints.app_factory instead.
This module provides backward compatibility for existing imports.
"""

import warnings

from endpoints.app_factory import create_demo_app, create_health_app
from endpoints.health_endpoints import setup_health_endpoints

warnings.warn(
    "Importing from 'health' is deprecated. Use 'endpoints.health_endpoints' and 'endpoints.app_factory' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["setup_health_endpoints", "create_health_app", "create_demo_app"]
