# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Factory for creating mock HTTP responses."""

from unittest.mock import MagicMock

import requests


class HttpResponseFactory:
    """Factory for creating mock HTTP responses with common configurations."""

    @staticmethod
    def success(
        content: str = "<html><body><h1>Test Page</h1></body></html>",
        content_type: str = "text/html; charset=utf-8",
        status_code: int = 200,
    ) -> MagicMock:
        """Create a successful HTTP response."""
        mock = MagicMock(spec=requests.Response)
        mock.status_code = status_code
        mock.content = content.encode("utf-8")
        mock.text = content
        mock.headers = {"Content-Type": content_type}
        mock.raise_for_status = MagicMock()  # Does nothing on success
        return mock

    @staticmethod
    def html_with_title(title: str, body: str = "Test content") -> MagicMock:
        """Create an HTML response with specific title."""
        html = f"<html><head><title>{title}</title></head><body>{body}</body></html>"
        return HttpResponseFactory.success(content=html)

    @staticmethod
    def plaintext(text: str = "Plain text content") -> MagicMock:
        """Create a plaintext response."""
        return HttpResponseFactory.success(content=text, content_type="text/plain")

    @staticmethod
    def pdf() -> MagicMock:
        """Create a PDF file response."""
        return HttpResponseFactory.success(
            content="%PDF-1.4 fake pdf content", content_type="application/pdf"
        )

    @staticmethod
    def error_404() -> MagicMock:
        """Create a 404 error response."""
        mock = MagicMock(spec=requests.Response)
        mock.status_code = 404
        mock.raise_for_status.side_effect = requests.HTTPError(
            "404 Client Error: Not Found"
        )
        return mock

    @staticmethod
    def timeout() -> MagicMock:
        """Create a mock that raises Timeout exception."""
        mock = MagicMock()
        mock.side_effect = requests.Timeout("Request timed out after 5 seconds")
        return mock

    @staticmethod
    def connection_error() -> MagicMock:
        """Create a mock that raises ConnectionError."""
        mock = MagicMock()
        mock.side_effect = requests.ConnectionError("Failed to establish connection")
        return mock
