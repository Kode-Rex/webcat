#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Test real MCP server with full handshake."""
import json

import requests

session = requests.Session()
base_url = "http://localhost:4000/mcp"

print("=== TESTING REAL MCP SERVER ON PORT 4000 ===\n")

# Step 1: Initialize
print("1. Initialize...")
init_resp = session.post(
    base_url,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    },
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"},
        },
    },
    stream=True,
)

session_id = init_resp.headers.get("mcp-session-id")
print(f"   Session: {session_id}")

# Step 2: Send initialized notification
print("2. Send initialized notification...")
notif_resp = session.post(
    base_url,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-session-id": session_id,
    },
    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
)
print(f"   Status: {notif_resp.status_code}")

# Step 3: Call search
print("3. Call search with max_results=2...")
resp = session.post(
    base_url,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Authorization": "Bearer sk-abc-123-def-456",
        "mcp-session-id": session_id,
    },
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "search",
            "arguments": {"query": "Python programming", "max_results": 2},
        },
    },
    stream=True,
    timeout=90,
)

print(f"   Status: {resp.status_code}\n")

for line in resp.iter_lines():
    if line:
        line_str = line.decode("utf-8")
        if line_str.startswith("data: "):
            data = json.loads(line_str[6:])

            if "error" in data:
                print("❌ Error:", data["error"])
                break
            elif "result" in data:
                result = json.loads(data["result"]["content"][0]["text"])

                print("✅ SUCCESS - REAL MCP SERVER!")
                print("\nQuery:", result["query"])
                print("Source:", result["search_source"])
                print("Results:", len(result["results"]))

                if len(result["results"]) == 2:
                    print("✅ max_results=2 WORKS!")
                else:
                    print("❌ Expected 2 results")

                for i, r in enumerate(result["results"], 1):
                    print(f"{i}. {r['title']}")
                    print(f"   {r['url']}")
                break
