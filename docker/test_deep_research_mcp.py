#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Test deep_research tool via MCP server."""

import json

import requests

MCP_SERVER_URL = "http://localhost:8000/mcp"

# Create session with required headers
session = requests.Session()
session.headers.update({"Accept": "application/json, text/event-stream"})

# Step 1: Initialize
print("🔧 Initializing MCP session...")
init_payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0.0"},
    },
}

init_resp = session.post(MCP_SERVER_URL, json=init_payload)
session_id = init_resp.headers.get("mcp-session-id")
print(f"✅ Session ID: {session_id}\n")

# Step 2: Send initialized notification
print("🔔 Sending initialized notification...")
initialized_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
session.post(
    MCP_SERVER_URL, json=initialized_payload, headers={"mcp-session-id": session_id}
)

# Step 3: Call deep_research tool
print("\n🔍 Calling deep_research tool...")
print("Query: What is Python programming language?")
print("Effort: low")
print("\nThis will take ~1-2 minutes...\n")

tool_payload = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "deep_research",
        "arguments": {
            "query": "What is Python programming language?",
            "research_effort": "low",
            "max_results": 5,
        },
    },
}

tool_resp = session.post(
    MCP_SERVER_URL,
    json=tool_payload,
    headers={"mcp-session-id": session_id},
    timeout=300,
)

print(f"Status: {tool_resp.status_code}\n")

# Parse SSE response
if tool_resp.status_code == 200:
    lines = tool_resp.text.strip().split("\n")
    for line in lines:
        if line.startswith("data: "):
            data_json = line[6:]  # Remove "data: " prefix
            result = json.loads(data_json)

            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    # Parse the JSON string inside text
                    research_result = json.loads(text_content)

                    print("=" * 80)
                    print("DEEP RESEARCH RESULT:")
                    print("=" * 80)
                    print(f"Query: {research_result.get('query')}")
                    print(f"Source: {research_result.get('search_source')}")
                    print(f"Results: {len(research_result.get('results', []))}")

                    if research_result.get("results"):
                        print("\n" + "=" * 80)
                        print("RESEARCH REPORT:")
                        print("=" * 80)
                        print(research_result["results"][0].get("content", ""))

            break
else:
    print(f"❌ Error: {tool_resp.text}")
