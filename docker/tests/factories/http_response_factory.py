# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Factory for creating HTTP response test doubles."""

import requests

from tests.factories.mock_http_response import MockHttpResponse


class HttpResponseFactory:
    """Factory for creating pre-configured HTTP response mocks."""

    @staticmethod
    def success(
        content: bytes = b"<html><body><p>Test content</p></body></html>",
        headers: dict = None,
    ) -> MockHttpResponse:
        """Create successful HTML response.

        Args:
            content: HTML content as bytes
            headers: Response headers

        Returns:
            MockHttpResponse with 200 status
        """
        default_headers = {"Content-Type": "text/html"}
        if headers:
            default_headers.update(headers)
        return MockHttpResponse(
            content=content, headers=default_headers, status_code=200
        )

    @staticmethod
    def plaintext(text: str = "Plain text content") -> MockHttpResponse:
        """Create plaintext response.

        Args:
            text: Plain text content

        Returns:
            MockHttpResponse with text/plain content type
        """
        return MockHttpResponse(
            content=text.encode(), text=text, headers={"Content-Type": "text/plain"}
        )

    @staticmethod
    def with_http_error(status_code: int, message: str) -> MockHttpResponse:
        """Create response that raises HTTPError.

        Args:
            status_code: HTTP status code
            message: Error message

        Returns:
            MockHttpResponse that raises on raise_for_status()
        """
        return MockHttpResponse(
            status_code=status_code,
            should_raise=requests.exceptions.HTTPError(message),
        )

    @staticmethod
    def connection_error(message: str = "Connection error"):
        """Create exception for connection error.

        Args:
            message: Error message

        Returns:
            RequestException to be used with side_effect
        """
        return requests.exceptions.RequestException(message)

    @staticmethod
    def timeout():
        """Create timeout exception.

        Returns:
            Timeout exception to be used with side_effect
        """
        return requests.exceptions.Timeout("Request timed out")

    @staticmethod
    def html_with_title(title: str) -> MockHttpResponse:
        """Create HTML response with specific title.

        Args:
            title: Page title

        Returns:
            MockHttpResponse with HTML content
        """
        html = f"<html><head><title>{title}</title></head><body><p>Content</p></body></html>"
        return MockHttpResponse(
            content=html.encode(), headers={"Content-Type": "text/html"}
        )

    @staticmethod
    def pdf() -> MockHttpResponse:
        """Create PDF response.

        Returns:
            MockHttpResponse with PDF content type
        """
        return MockHttpResponse(
            content=b"%PDF-1.4", headers={"Content-Type": "application/pdf"}
        )

    @staticmethod
    def error_404() -> MockHttpResponse:
        """Create 404 error response.

        Returns:
            MockHttpResponse that raises 404 HTTPError
        """
        return MockHttpResponse(
            status_code=404,
            should_raise=requests.exceptions.HTTPError("404 Not Found"),
        )
