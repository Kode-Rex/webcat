# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Centralized logging configuration for WebCat."""

import logging
import logging.handlers
import os
import tempfile
from typing import Optional

from constants import (
    DEFAULT_LOG_FILE,
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_BYTES,
)


def setup_logging(
    log_file_name: str = DEFAULT_LOG_FILE, logger_name: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging with console and rotating file handlers.

    Args:
        log_file_name: Name of the log file (e.g., "webcat.log", "webcat_demo.log")
        logger_name: Name of the logger (None for root logger)

    Returns:
        Configured logger instance
    """
    # Get configuration from environment
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    log_dir: str = os.environ.get("LOG_DIR", tempfile.gettempdir())
    log_file: str = os.path.join(log_dir, log_file_name)

    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Configure logger
    logger: logging.Logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Setup rotating file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logging initialized with file rotation at {log_file}")
    return logger
