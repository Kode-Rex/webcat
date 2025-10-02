# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Factory for creating typed mock HTTP responses - no raw MagicMock."""

import requests

from tests.factories.mock_http_response import MockHttpResponse


class HttpResponseFactory:
    """
    Factory for creating typed mock HTTP responses.

    Returns proper test doubles, not MagicMock with property assignment.
    Each method returns a fully-configured MockHttpResponse instance.
    """

    @staticmethod
    def success(
        content: str = "<html><body><h1>Test Page</h1></body></html>",
        content_type: str = "text/html; charset=utf-8",
        status_code: int = 200,
    ) -> MockHttpResponse:
        """Create a successful HTTP response."""
        return MockHttpResponse(
            status_code=status_code,
            content=content.encode("utf-8"),
            text=content,
            headers={"Content-Type": content_type},
            should_raise_for_status=False,
        )

    @staticmethod
    def html_with_title(title: str, body: str = "Test content") -> MockHttpResponse:
        """Create an HTML response with specific title."""
        html = f"<html><head><title>{title}</title></head><body>{body}</body></html>"
        return HttpResponseFactory.success(content=html)

    @staticmethod
    def plaintext(text: str = "Plain text content") -> MockHttpResponse:
        """Create a plaintext response."""
        return HttpResponseFactory.success(content=text, content_type="text/plain")

    @staticmethod
    def pdf() -> MockHttpResponse:
        """Create a PDF file response."""
        return HttpResponseFactory.success(
            content="%PDF-1.4 fake pdf content", content_type="application/pdf"
        )

    @staticmethod
    def error_404() -> MockHttpResponse:
        """Create a 404 error response."""
        return MockHttpResponse(
            status_code=404,
            content=b"Not Found",
            text="Not Found",
            headers={"Content-Type": "text/html"},
            should_raise_for_status=True,
            raise_on_access=requests.HTTPError("404 Client Error: Not Found"),
        )

    @staticmethod
    def error_500() -> MockHttpResponse:
        """Create a 500 error response."""
        return MockHttpResponse(
            status_code=500,
            content=b"Internal Server Error",
            text="Internal Server Error",
            headers={"Content-Type": "text/html"},
            should_raise_for_status=True,
            raise_on_access=requests.HTTPError("500 Server Error"),
        )

    @staticmethod
    def timeout() -> Exception:
        """
        Create a Timeout exception.

        Usage:
            mock_get.side_effect = HttpResponseFactory.timeout()
        """
        return requests.Timeout("Request timed out after 5 seconds")

    @staticmethod
    def connection_error() -> Exception:
        """
        Create a ConnectionError exception.

        Usage:
            mock_get.side_effect = HttpResponseFactory.connection_error()
        """
        return requests.ConnectionError("Failed to establish connection")
