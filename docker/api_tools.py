# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""API tools module for FastMCP WebCat integration.

DEPRECATED: Import from tools.api_tools_setup instead.
This module provides backward compatibility for existing imports.
"""

import warnings

from tools.api_tools_setup import create_webcat_functions, setup_webcat_tools

warnings.warn(
    "Importing from 'api_tools' is deprecated. Use 'tools.api_tools_setup' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["setup_webcat_tools", "create_webcat_functions"]
