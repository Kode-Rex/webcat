#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Debug version - shows exactly what Perplexity returns."""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")

if not PERPLEXITY_API_KEY:
    print("❌ PERPLEXITY_API_KEY not set")
    sys.exit(1)

print(f"✅ API Key: {PERPLEXITY_API_KEY[:8]}...\n")

url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": "sonar-deep-research",
    "messages": [{"role": "user", "content": "What is Python programming language?"}],
    "reasoning_effort": "low",
    "return_citations": True,
}

print("Making API call (this will cost ~$1)...")
print(f"Query: {payload['messages'][0]['content']}")
print(f"Effort: {payload['reasoning_effort']}\n")

response = requests.post(url, headers=headers, json=payload, timeout=300)

print(f"Status: {response.status_code}")
print(f"Response keys: {list(response.json().keys())}\n")

data = response.json()

# Show full response structure
print("=" * 80)
print("FULL RESPONSE:")
print("=" * 80)
print(json.dumps(data, indent=2))
