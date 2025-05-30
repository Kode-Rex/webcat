#!/usr/bin/env python3
"""Debug script to test the search functionality directly."""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_search():
    """Test direct search with Serper API."""
    print("🔍 Testing search functionality with Serper API...")
    
    # Get API key from environment
    api_key = os.environ.get("SERPER_API_KEY", "")
    if not api_key:
        api_key = os.environ.get("WEBCAT_API_KEY", "")
        
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
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    query = "What is the capital of France?"
    payload = {
        'q': query,
        'gl': 'us',
        'hl': 'en'
    }
    
    print(f"🔎 Searching for: '{query}'")
    
    try:
        # Make the request to Serper API
        print(f"📡 Sending request to: {serper_url}")
        response = requests.post(serper_url, headers=headers, json=payload)
        
        print(f"📊 Status code: {response.status_code}")
        
        # Check if the response is successful
        if response.status_code == 200:
            search_results = response.json()
            
            # Check if organic results are present
            if 'organic' in search_results and search_results['organic']:
                print(f"✅ Success! Found {len(search_results['organic'])} organic results")
                # Print the first result
                first_result = search_results['organic'][0]
                print(f"\nFirst result:")
                print(f"Title: {first_result.get('title', 'No title')}")
                print(f"Link: {first_result.get('link', 'No link')}")
                print(f"Snippet: {first_result.get('snippet', 'No snippet')}")
            else:
                print("❌ No organic results found in the response")
                print(f"Response content: {json.dumps(search_results, indent=2)}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        
if __name__ == "__main__":
    debug_search() 