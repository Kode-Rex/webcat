# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Typed mock for HTTP responses."""

from typing import Any, Dict, Optional


class MockHttpResponse:
    """Typed mock for HTTP response objects."""

    def __init__(
        self,
        content: bytes = b"",
        text: str = "",
        headers: Optional[Dict[str, str]] = None,
        status_code: int = 200,
        should_raise: Optional[Exception] = None,
    ):
        """Initialize mock HTTP response.

        Args:
            content: Response body as bytes
            text: Response body as text
            headers: Response headers
            status_code: HTTP status code
            should_raise: Exception to raise on raise_for_status()
        """
        self.content = content
        self.text = text
        self.headers = headers or {}
        self.status_code = status_code
        self._should_raise = should_raise

    def raise_for_status(self) -> None:
        """Raise exception if configured."""
        if self._should_raise:
            raise self._should_raise

    def json(self) -> Dict[str, Any]:
        """Return empty dict for JSON responses."""
        return {}
