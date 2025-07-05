#!/usr/bin/env python3
"""
Test script to check what endpoints are actually available on the server.
"""

import requests
import json

def test_endpoints():
    """Test various endpoint patterns to see what works."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing MCP endpoints...")
    print("=" * 40)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Check health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
    
    # Test 3: Check MCP tools endpoint
    try:
        response = requests.get(f"{base_url}/mcp/tools")
        print(f"✅ MCP tools endpoint: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MCP tools endpoint failed: {e}")
    
    # Test 4: Check MCP tools list
    try:
        response = requests.get(f"{base_url}/mcp/tools/list")
        print(f"✅ MCP tools list endpoint: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MCP tools list endpoint failed: {e}")
    
    # Test 5: Check MCP tools call endpoint
    try:
        response = requests.post(f"{base_url}/mcp/tools/call", 
                               json={"name": "search_web", "arguments": {"query": "test"}})
        print(f"✅ MCP tools call endpoint: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MCP tools call endpoint failed: {e}")
    
    # Test 6: Check the specific search_web endpoint
    try:
        response = requests.post(f"{base_url}/mcp/tools/search_web", 
                               json={"query": "test", "num_results": 1})
        print(f"✅ Search web endpoint: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Search web endpoint failed: {e}")
    
    # Test 7: Check with proper MCP format
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "search_web",
                "arguments": {
                    "query": "test",
                    "num_results": 1
                }
            }
        }
        response = requests.post(f"{base_url}/mcp/tools/call", 
                               json=mcp_request,
                               headers={"Content-Type": "application/json"})
        print(f"✅ MCP tools call with proper format: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ MCP tools call with proper format failed: {e}")

if __name__ == "__main__":
    test_endpoints() 