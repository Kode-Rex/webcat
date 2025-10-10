#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import json

import requests

session = requests.Session()
base_url = "http://localhost:4001/mcp"

print("=== TESTING PORT 4001 WITH DEBUG LOGGING ===\n")

# Initialize
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
print(f"Session: {session_id}\n")

# Send initialized
session.post(
    base_url,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "mcp-session-id": session_id,
    },
    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
)

# Call search
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
            "arguments": {"query": "Python", "max_results": 2},
        },
    },
    stream=True,
    timeout=90,
)

print(f"Status: {resp.status_code}\n")

for line in resp.iter_lines():
    if line and line.decode("utf-8").startswith("data: "):
        data = json.loads(line.decode("utf-8")[6:])
        if "result" in data:
            result = json.loads(data["result"]["content"][0]["text"])
            print(f"✅ Query: {result['query']}")
            print(f"   Source: {result['search_source']}")
            print(f"   Results: {len(result['results'])}")
            if result.get("error"):
                print(f"   Error: {result['error']}")
            break
