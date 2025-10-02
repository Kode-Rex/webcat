# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Typed mock HTTP response - no raw property assignment."""

from typing import Dict, Optional

import requests


class MockHttpResponse:
    """
    Typed mock for HTTP responses.

    This is a proper test double, not a MagicMock with property assignment.
    All properties are set via constructor for immutability and type safety.
    """

    def __init__(
        self,
        status_code: int = 200,
        content: bytes = b"<html><body><h1>Test Page</h1></body></html>",
        text: str = "<html><body><h1>Test Page</h1></body></html>",
        headers: Optional[Dict[str, str]] = None,
        should_raise_for_status: bool = False,
        raise_on_access: Optional[Exception] = None,
    ):
        """
        Create a mock HTTP response.

        Args:
            status_code: HTTP status code
            content: Response content as bytes
            text: Response content as text
            headers: Response headers dict
            should_raise_for_status: Whether raise_for_status() should raise
            raise_on_access: Exception to raise when accessed (for timeout/connection errors)
        """
        self.status_code = status_code
        self.content = content
        self.text = text
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8"}
        self._should_raise = should_raise_for_status
        self._raise_on_access = raise_on_access

    def raise_for_status(self) -> None:
        """Mock of requests.Response.raise_for_status()."""
        if self._raise_on_access:
            raise self._raise_on_access
        if self._should_raise:
            raise requests.HTTPError(f"{self.status_code} Error")

    @property
    def ok(self) -> bool:
        """Mock of requests.Response.ok property."""
        return 200 <= self.status_code < 300

    def json(self) -> dict:
        """Mock of requests.Response.json()."""
        import json

        return json.loads(self.text)
