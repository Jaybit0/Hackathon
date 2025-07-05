#!/usr/bin/env python3
"""
Test script for the Intelligent Search Tool.
"""

import os
import sys
from dotenv import load_dotenv

# Import the intelligent search tool
from intelligent_search_tool import IntelligentSearchTool


def test_intelligent_search():
    """Test the intelligent search tool."""
    
    print("🧪 Testing Intelligent Search Tool")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in your .env file")
        return False
    
    # Initialize the tool
    try:
        tool = IntelligentSearchTool()
        print("✅ Intelligent search tool initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize tool: {e}")
        return False
    
    # Test queries
    test_queries = [
        "What is machine learning?",
        "Python programming basics",
        "OpenAI GPT features"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            # Perform intelligent search
            results = tool.intelligent_search(query, max_sites=2)
            
            if results.get('success'):
                print("✅ Intelligent search completed successfully!")
                
                # Show statistics
                initial_count = len(results.get('initial_results', []))
                selected_count = len(results.get('selected_sites', []))
                extracted_count = len([c for c in results.get('extracted_content', []) if c.get('extraction_success')])
                
                print(f"📊 Statistics:")
                print(f"   • Initial results: {initial_count}")
                print(f"   • Sites selected by LLM: {selected_count}")
                print(f"   • Content extracted: {extracted_count}")
                
                # Show summary preview
                summary = results.get('summary', '')
                if summary:
                    preview = summary[:200] + "..." if len(summary) > 200 else summary
                    print(f"📝 Summary preview: {preview}")
                
            else:
                print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during search: {e}")
        
        print()
    
    print("✅ All tests completed!")
    return True


def test_mcp_connection():
    """Test MCP server connection."""
    print("🔗 Testing MCP server connection...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP server is running")
            return True
        else:
            print(f"❌ MCP server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ MCP server is not running")
        print("Start it with: ./start_openai_mcp.sh")
        return False
    except Exception as e:
        print(f"❌ Error checking MCP server: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Intelligent Search Tool Test")
    print("=" * 50)
    
    # Test MCP connection first
    if not test_mcp_connection():
        print("\n💡 To start the MCP server:")
        print("   ./start_openai_mcp.sh")
        print("   or")
        print("   conda activate hackathon && uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # Test the intelligent search tool
    if test_intelligent_search():
        print("\n🎉 All tests passed!")
        print("\n💡 You can now use the intelligent search tool:")
        print("   python interactive_intelligent_search.py")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main() 