#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Simple test script for the demo server components."""

import threading
import time

import uvicorn


def test_health_server():
    """Test just the health server."""
    from health import create_health_app

    print("Creating health app...")
    app = create_health_app()

    print("Starting health server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")


def test_main_server():
    """Test just the main server."""
    import asyncio

    from demo_server import run_server

    print("Creating main server...")
    app = asyncio.run(run_server())

    print("Starting main server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


def test_both_servers():
    """Test both servers together."""

    def run_health():
        print("Starting health server thread...")
        test_health_server()

    # Start health server in background
    health_thread = threading.Thread(target=run_health, daemon=True)
    health_thread.start()

    print("Waiting for health server to start...")
    time.sleep(2)

    print("Starting main server...")
    test_main_server()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "health":
            test_health_server()
        elif mode == "main":
            test_main_server()
        elif mode == "both":
            test_both_servers()
        else:
            print("Usage: python test_demo.py [health|main|both]")
    else:
        print("Testing both servers...")
        test_both_servers()
