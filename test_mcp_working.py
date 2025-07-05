#!/usr/bin/env python3
"""
Test script to verify MCP tool is working with test entries.
"""

import requests
import json
import sys

def test_mcp_search():
    """Test the MCP search tool to verify it's working."""
    
    print("🧪 Testing MCP Search Tool")
    print("=" * 40)
    
    # Test data
    test_queries = [
        "test query",
        "python programming",
        "openai gpt",
        "random search term"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: '{query}'")
        print("-" * 30)
        
        # Make request to MCP server
        request_data = {
            "jsonrpc": "2.0",
            "id": i,
            "method": "tools/call",
            "params": {
                "name": "search_web",
                "arguments": {
                    "query": query,
                    "num_results": 3
                }
            }
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/mcp/tools/search_web",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse the results
                if "result" in result and "content" in result["result"]:
                    content = result["result"]["content"]
                    if content and len(content) > 0 and "text" in content[0]:
                        search_results = json.loads(content[0]["text"])
                        
                        print(f"✅ Success! Found {len(search_results)} results:")
                        
                        for j, result_item in enumerate(search_results, 1):
                            if "error" in result_item:
                                print(f"  {j}. ❌ Error: {result_item['error']}")
                            else:
                                title = result_item.get("title", "No title")
                                link = result_item.get("link", "No link")
                                snippet = result_item.get("snippet", "No snippet")
                                
                                print(f"  {j}. 📄 {title}")
                                print(f"     🔗 {link}")
                                print(f"     📝 {snippet[:100]}{'...' if len(snippet) > 100 else ''}")
                        
                        # Check if test entry is present
                        test_entries = [r for r in search_results if "🧪 MCP Test Entry" in r.get("title", "")]
                        if test_entries:
                            print(f"  ✅ Test entry found: {len(test_entries)} test entries")
                        else:
                            print(f"  ⚠️  No test entries found")
                    else:
                        print("❌ Invalid response format")
                else:
                    print("❌ No result content in response")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: MCP server not running")
            print("Start the server with: ./start_openai_mcp.sh")
        except requests.exceptions.Timeout:
            print("❌ Timeout: Request took too long")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 40)
    print("🎯 Test Summary:")
    print("• If you see test entries with 🧪, the MCP tool is working!")
    print("• Test entries should appear even if Google API is not configured")
    print("• You can now use this with your OpenAI client")

def test_server_status():
    """Test if the server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP server is running")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ MCP server is not running")
        print("Start it with: ./start_openai_mcp.sh")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MCP Tool Test Script")
    print("=" * 40)
    
    # Check if server is running
    if test_server_status():
        # Run the search tests
        test_mcp_search()
    else:
        print("\n💡 To start the server:")
        print("   ./start_openai_mcp.sh")
        print("   or")
        print("   conda activate hackathon && uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload") 