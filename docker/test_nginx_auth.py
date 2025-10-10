# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Test nginx auth proxy - both with and without bearer token."""


import requests

base_url = "http://localhost:8000/mcp"

# Load API key from .env
with open(".env") as f:
    for line in f:
        if line.startswith("WEBCAT_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break

print("=" * 60)
print("Test 1: Without Authorization header (should fail)")
print("=" * 60)

session = requests.Session()
session.headers.update({"Accept": "application/json, text/event-stream"})

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

try:
    resp = session.post(base_url, json=init_payload, timeout=5)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
    if resp.status_code == 401:
        print("✅ Auth correctly blocked request without token")
    else:
        print(f"⚠️  Expected 401 but got {resp.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test 2: With valid Authorization header (should succeed)")
print("=" * 60)

session2 = requests.Session()
session2.headers.update(
    {
        "Accept": "application/json, text/event-stream",
        "Authorization": f"Bearer {api_key}",
    }
)

try:
    resp = session2.post(base_url, json=init_payload, timeout=5)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Auth correctly allowed request with valid token")
        session_id = resp.headers.get("mcp-session-id")
        print(f"Session ID: {session_id}")

        # Try a search
        print("\nTest 3: Real search with max_results=1")
        notif_resp = session2.post(
            base_url,
            json={"jsonrpc": "2.0", "method": "notifications/initialized"},
            headers={"mcp-session-id": session_id},
            timeout=5,
        )

        search_resp = session2.post(
            base_url,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "search",
                    "arguments": {"query": "MCP protocol", "max_results": 1},
                },
            },
            headers={"mcp-session-id": session_id},
            timeout=30,
        )

        if search_resp.status_code == 200:
            print(f"Search status: {search_resp.status_code}")
            # Parse SSE
            import json

            for line in search_resp.text.strip().split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "result" in data:
                        content_text = data["result"]["content"][0]["text"]
                        search_data = json.loads(content_text)
                        results = search_data.get("results", [])
                        print(f"✅ Got {len(results)} result(s) with max_results=1")
                        if results:
                            print(f"   Title: {results[0]['title']}")
                            print(f"   URL: {results[0]['url'][:50]}...")
                    break
        else:
            print(f"⚠️  Search failed: {search_resp.status_code}")
    else:
        print(f"⚠️  Expected 200 but got {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")
