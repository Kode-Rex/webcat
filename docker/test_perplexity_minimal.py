#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Minimal test to verify Perplexity API is being called."""

import json
import os
import sys

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

if not PERPLEXITY_API_KEY:
    print("❌ PERPLEXITY_API_KEY not set")
    sys.exit(1)

print(f"✅ API Key found: {PERPLEXITY_API_KEY[:8]}...")

# Minimal API call
url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json",
}

# Start with absolute minimal payload
payload = {
    "model": "sonar-deep-research",
    "messages": [{"role": "user", "content": "What is Python?"}],
}

print("\n🔍 Testing minimal Perplexity API call...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

try:
    print("📡 Making request...")
    response = requests.post(url, headers=headers, json=payload, timeout=300)
    print(f"✅ Response status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Got response with {len(json.dumps(data))} chars")
        print(f"\nResponse structure: {list(data.keys())}")
        if "choices" in data:
            print(f"Choices: {len(data['choices'])}")
            if data["choices"]:
                content = data["choices"][0].get("message", {}).get("content", "")
                print(f"Content length: {len(content)} chars")
                print(f"\nFirst 500 chars:\n{content[:500]}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback

    traceback.print_exc()
