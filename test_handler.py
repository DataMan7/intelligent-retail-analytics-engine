#!/usr/bin/env python3
"""
Test the Vercel handler function locally
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from api.index import handler

def test_handler():
    """Test the handler function"""

    # Test root path
    event = {
        "path": "/",
        "httpMethod": "GET"
    }
    context = {}

    print("Testing handler with root path...")
    result = handler(event, context)
    print(f"Status: {result['statusCode']}")
    print(f"Content-Type: {result['headers']['Content-Type']}")
    print(f"Body length: {len(result['body'])}")
    print("Body preview:", result['body'][:200] + "...")

    # Test API endpoint
    event2 = {
        "path": "/api/test/health",
        "httpMethod": "GET"
    }

    print("\nTesting handler with API path...")
    result2 = handler(event2, context)
    print(f"Status: {result2['statusCode']}")
    print(f"Content-Type: {result2['headers']['Content-Type']}")
    print("Body:", result2['body'])

if __name__ == "__main__":
    test_handler()