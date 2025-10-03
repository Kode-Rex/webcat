# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for logging configuration."""

import logging
import os

from utils.logging_config import setup_logging


class TestLoggingConfig:
    """Tests for logging configuration."""

    def test_returns_logger_instance(self):
        # Act
        logger = setup_logging("test.log")

        # Assert
        assert isinstance(logger, logging.Logger)

    def test_creates_log_file(self, temp_test_dir):
        # Arrange
        os.environ["LOG_DIR"] = str(temp_test_dir)

        # Act
        setup_logging("test.log")

        # Assert
        log_file = temp_test_dir / "test.log"
        assert log_file.exists()

    def test_sets_log_level_from_environment(self):
        # Arrange
        os.environ["LOG_LEVEL"] = "DEBUG"

        # Act
        logger = setup_logging("test_debug.log")

        # Assert
        assert logger.level == logging.DEBUG

    def test_uses_default_log_level(self):
        # Arrange
        os.environ.pop("LOG_LEVEL", None)

        # Act
        logger = setup_logging("test_default.log")

        # Assert
        assert logger.level == logging.INFO

    def test_logger_has_handlers(self):
        # Act
        logger = setup_logging("test_handlers.log")

        # Assert
        assert len(logger.handlers) >= 2  # Console + File handler
