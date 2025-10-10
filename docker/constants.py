# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Constants for WebCat application."""

import os

# Application version
VERSION = "2.3.1"

# Service information
SERVICE_NAME = "WebCat MCP Server"
SERVICE_DESCRIPTION = "Web search and content extraction with MCP protocol support"

# Server capabilities
CAPABILITIES = [
    "Web search with Serper API",
    "DuckDuckGo fallback search",
    "Content extraction and scraping",
    "Markdown conversion",
    "FastMCP protocol support",
]

# Content limits
try:
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", "1000000"))
except ValueError:
    MAX_CONTENT_LENGTH = 1000000
DEFAULT_SEARCH_RESULTS = 5

# Timeout settings
REQUEST_TIMEOUT_SECONDS = 5
HEARTBEAT_INTERVAL_SECONDS = 30

# Logging
DEFAULT_LOG_FILE = "webcat.log"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5
