# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Demo client endpoint handlers."""

import logging
from pathlib import Path

from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger(__name__)


def client_not_found_response(client_path: Path) -> JSONResponse:
    """Create response for missing client file."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "WebCat client file not found",
            "expected_path": str(client_path),
            "exists": False,
        },
    )


def client_error_response(error: str) -> JSONResponse:
    """Create response for client loading error."""
    return JSONResponse(
        status_code=500,
        content={"error": "Failed to serve WebCat client", "details": error},
    )


def load_client_file(client_path: Path) -> HTMLResponse:
    """Load and return client HTML file."""
    html_content = client_path.read_text(encoding="utf-8")
    logger.info("Successfully loaded WebCat demo client")
    return HTMLResponse(content=html_content)


def serve_demo_client():
    """Serve the WebCat SSE demo client."""
    try:
        current_dir = Path(__file__).parent
        client_path = current_dir.parent.parent / "examples" / "webcat_client.html"
        logger.info(f"Looking for client file at: {client_path}")

        if client_path.exists():
            return load_client_file(client_path)

        logger.error(f"WebCat client file not found at: {client_path}")
        return client_not_found_response(client_path)
    except Exception as e:
        logger.error(f"Failed to serve WebCat client: {str(e)}")
        return client_error_response(str(e))
