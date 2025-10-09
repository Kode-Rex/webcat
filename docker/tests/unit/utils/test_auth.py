# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Unit tests for authentication utilities."""

from unittest.mock import patch

from utils.auth import validate_bearer_token


class TestValidateBearerToken:
    """Tests for validate_bearer_token function."""

    @patch.dict("os.environ", {}, clear=True)
    def test_no_auth_required_when_api_key_not_set(self):
        """When WEBCAT_API_KEY is not set, authentication should pass."""
        # Act
        is_valid, error_msg = validate_bearer_token(ctx=None)

        # Assert
        assert is_valid is True
        assert error_msg is None

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_fails_when_context_is_none(self):
        """When API key is set but no context provided, should fail."""
        # Act
        is_valid, error_msg = validate_bearer_token(ctx=None)

        # Assert
        assert is_valid is False
        assert "missing bearer token" in error_msg.lower()

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_fails_when_no_headers_in_context(self):
        """When API key is set but context has no headers, should fail."""
        # Arrange
        ctx = {}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is False
        assert "missing bearer token" in error_msg.lower()

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_fails_when_authorization_header_missing(self):
        """When API key is set but Authorization header missing, should fail."""
        # Arrange
        ctx = {"headers": {}}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is False
        assert "authorization" in error_msg.lower()

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_fails_when_authorization_header_invalid_format(self):
        """When Authorization header has invalid format, should fail."""
        # Arrange
        ctx = {"headers": {"Authorization": "InvalidFormat"}}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is False
        assert "invalid authorization header format" in error_msg.lower()

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_fails_when_bearer_keyword_missing(self):
        """When Authorization header doesn't start with Bearer, should fail."""
        # Arrange
        ctx = {"headers": {"Authorization": "Basic test-token"}}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is False
        assert "invalid authorization header format" in error_msg.lower()

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_fails_when_token_is_incorrect(self):
        """When token doesn't match WEBCAT_API_KEY, should fail."""
        # Arrange
        ctx = {"headers": {"Authorization": "Bearer wrong-token"}}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is False
        assert "invalid bearer token" in error_msg.lower()

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_succeeds_when_token_is_correct(self):
        """When token matches WEBCAT_API_KEY, should succeed."""
        # Arrange
        ctx = {"headers": {"Authorization": "Bearer test-token"}}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is True
        assert error_msg is None

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_handles_case_insensitive_authorization_header(self):
        """Should handle Authorization header with different cases."""
        # Test lowercase
        ctx = {"headers": {"authorization": "Bearer test-token"}}
        is_valid, error_msg = validate_bearer_token(ctx=ctx)
        assert is_valid is True
        assert error_msg is None

        # Test uppercase
        ctx = {"headers": {"AUTHORIZATION": "Bearer test-token"}}
        is_valid, error_msg = validate_bearer_token(ctx=ctx)
        assert is_valid is True
        assert error_msg is None

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_handles_context_with_headers_attribute(self):
        """Should extract headers from context.headers attribute."""

        # Arrange
        class ContextWithAttribute:
            def __init__(self):
                self.headers = {"Authorization": "Bearer test-token"}

        ctx = ContextWithAttribute()

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is True
        assert error_msg is None

    @patch.dict(
        "os.environ", {"WEBCAT_API_KEY": "test-token"}, clear=True
    )  # pragma: allowlist secret
    def test_bearer_keyword_is_case_insensitive(self):
        """Bearer keyword should be case-insensitive."""
        # Arrange
        ctx = {"headers": {"Authorization": "bearer test-token"}}

        # Act
        is_valid, error_msg = validate_bearer_token(ctx=ctx)

        # Assert
        assert is_valid is True
        assert error_msg is None
