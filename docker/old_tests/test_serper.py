#!/usr/bin/env python3
# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Test script for the Serper API."""

import json
import os

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_serper_api():
    """Test direct search with Serper API."""
    print("🔍 Testing search functionality with Serper API...")

    # Get API key from environment
    api_key = os.environ.get("SERPER_API_KEY", "")

    if not api_key:
        print("❌ No API key found in environment variables.")
        return

    # Mask the key for display
    key_length = len(api_key)
    if key_length > 8:
        masked_key = f"{api_key[:4]}{'*' * (key_length - 8)}{api_key[-4:]}"
    else:
        masked_key = "****"
    print(f"🔑 Using API key: {masked_key}")

    # Configure the Serper API request
    serper_url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    query = "What is the capital of France?"
    payload = {"q": query, "gl": "us", "hl": "en"}

    print(f"🔎 Searching for: '{query}'")

    try:
        response = requests.post(serper_url, headers=headers, json=payload)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response received:")
            # Print only a portion of the response to avoid clutter
            if "organic" in result and result["organic"]:
                print(f"Found {len(result['organic'])} organic results")
                first_result = result["organic"][0]
                print(f"First result: {json.dumps(first_result, indent=2)}")
            else:
                print("No organic results found.")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


if __name__ == "__main__":
    test_serper_api()
