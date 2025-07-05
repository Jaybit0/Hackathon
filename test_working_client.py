#!/usr/bin/env python3
"""
Test client for the working search server.
"""

import requests
import json
import time
from typing import Dict, Any


class WorkingMCPClient:
    """Test client for the working MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.request_id = 1
    
    def test_search(self, query: str, num_results: int = 3):
        """Test the search_web tool."""
        print(f"\n🧪 Testing search with query: '{query}'")
        print("=" * 50)
        
        # Try different endpoint patterns
        endpoints_to_try = [
            f"{self.base_url}/mcp/tools/search_web",
            f"{self.base_url}/mcp/tools/call",
            f"{self.base_url}/mcp/tools"
        ]
        
        for endpoint in endpoints_to_try:
            print(f"🔍 Trying endpoint: {endpoint}")
            
            # Try different request formats
            request_formats = [
                # Format 1: Direct tool call
                {
                    "query": query,
                    "num_results": num_results
                },
                # Format 2: MCP JSON-RPC format
                {
                    "jsonrpc": "2.0",
                    "id": self.request_id,
                    "method": "tools/call",
                    "params": {
                        "name": "search_web",
                        "arguments": {
                            "query": query,
                            "num_results": num_results
                        }
                    }
                },
                # Format 3: Simple tool call
                {
                    "name": "search_web",
                    "arguments": {
                        "query": query,
                        "num_results": num_results
                    }
                }
            ]
            
            for i, request_data in enumerate(request_formats, 1):
                try:
                    print(f"  📝 Trying format {i}...")
                    
                    response = self.session.post(
                        endpoint,
                        json=request_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"  📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✅ Success! Response: {json.dumps(result, indent=2)}")
                        return result
                    else:
                        print(f"  ❌ Failed: {response.text}")
                        
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            
            print(f"  ⏭️  Moving to next endpoint...")
        
        print("❌ All endpoints and formats failed")
        return None


def main():
    """Main test function."""
    print("🚀 Working MCP Test Client")
    print("=" * 30)
    
    # Initialize client
    client = WorkingMCPClient()
    
    # Test cases
    test_queries = [
        "OpenAI GPT-4 features",
        "Python programming tips"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        result = client.test_search(query, num_results=2)
        
        # Wait a bit between requests
        if i < len(test_queries):
            print("⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    print("\n✅ All tests completed!")
    print("\n📊 Check the logs with:")
    print("   python view_logs.py --tail")
    print("   python view_logs.py --stats")


if __name__ == "__main__":
    main() 