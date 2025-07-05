#!/usr/bin/env python3
"""
Simple MCP Test Client

This script demonstrates how to make MCP requests to the search server
and see the logging in action.
"""

import requests
import json
import time
from typing import Dict, Any


class MCPTestClient:
    """Simple MCP client for testing."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.request_id = 1
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Response from the tool
        """
        request_data = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        self.request_id += 1
        
        try:
            print(f"🔍 Making MCP request to {tool_name}...")
            print(f"📝 Arguments: {json.dumps(arguments, indent=2)}")
            
            response = self.session.post(
                f"{self.base_url}/mcp/tools/search_web",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Response received:")
            print(f"📄 Result: {json.dumps(result, indent=2)}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return {"error": str(e)}
    
    def test_search(self, query: str, num_results: int = 3):
        """Test the search_web tool."""
        print(f"\n🧪 Testing search with query: '{query}'")
        print("=" * 50)
        
        result = self.call_tool("search_web", {
            "query": query,
            "num_results": num_results
        })
        
        return result


def main():
    """Main test function."""
    print("🚀 MCP Test Client")
    print("=" * 30)
    
    # Initialize client
    client = MCPTestClient()
    
    # Test cases
    test_queries = [
        "OpenAI GPT-4 features",
        "Python programming tips",
        "Machine learning basics"
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