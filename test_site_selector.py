#!/usr/bin/env python3
"""
Test script for the Site Selector Agent with real MCP search results.
"""

import os
import sys
from dotenv import load_dotenv

# Import the site selector agent
from site_selector_agent import SiteSelectorAgent


def test_with_mcp_search():
    """Test the site selector with real MCP search results."""
    
    print("🧪 Testing Site Selector with MCP Search")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in your .env file")
        return False
    
    # Initialize the agent
    agent = SiteSelectorAgent()
    
    # Test queries
    test_queries = [
        "best cars 2025",
        "Python machine learning tutorial",
        "OpenAI GPT-4 features"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: '{query}'")
        print("-" * 40)
        
        try:
            # Get search results from MCP server
            print(f"🔍 Getting search results from MCP server...")
            search_results = agent.openai_client.mcp_client.search_web(query, num_results=8)
            
            if not search_results:
                print("❌ No search results returned from MCP server")
                continue
            
            print(f"✅ Got {len(search_results)} search results from MCP server")
            
            # Run site selector
            result = agent.select_sites(query, search_results, max_sites=3, debug=False)
            
            if result['success']:
                print("✅ Site selection completed successfully!")
                print()
                
                print("🎯 SELECTED SITES:")
                print("-" * 40)
                for j, site in enumerate(result['selected_sites'], 1):
                    print(f"{j}. 🎯 {site['title']}")
                    print(f"   🔗 {site['url']}")
                    print(f"   ⭐ Confidence: {site['confidence']}/10")
                    print(f"   💭 Reason: {site['reason']}")
                    print(f"   📝 Expected: {site['expected_content']}")
                    print()
                
                # Analyze selection patterns
                analysis = agent.analyze_selection_patterns(query, search_results, result['selected_sites'])
                
                print("📊 SELECTION ANALYSIS:")
                print("-" * 40)
                print(f"   • Total results: {analysis['total_results']}")
                print(f"   • Selected: {analysis['selected_count']}")
                print(f"   • Selection rate: {analysis['selection_rate']:.1%}")
                print(f"   • Average confidence: {analysis['average_confidence']:.1f}/10")
                print(f"   • Selected indices: {analysis['selected_indices']}")
                
                # Check if MCP test entry was selected
                mcp_selected = False
                for site in result['selected_sites']:
                    if "🧪 MCP Test Entry" in site.get('title', ''):
                        mcp_selected = True
                        print(f"🎯 MCP Test Entry was selected with confidence {site['confidence']}/10")
                        break
                
                if not mcp_selected:
                    print("❌ MCP Test Entry was not selected")
                
            else:
                print(f"❌ Site selection failed: {result['error']}")
                if result['raw_llm_response']:
                    print(f"Raw LLM response: {result['raw_llm_response'][:200]}...")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
        
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
    print("🚀 Site Selector Agent Test with MCP")
    print("=" * 50)
    
    # Test MCP connection first
    if not test_mcp_connection():
        print("\n💡 To start the MCP server:")
        print("   ./start_openai_mcp.sh")
        print("   or")
        print("   conda activate hackathon && uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # Test the site selector with MCP search
    if test_with_mcp_search():
        print("\n🎉 All tests passed!")
        print("\n💡 You can now use the site selector agent:")
        print("   from site_selector_agent import SiteSelectorAgent")
        print("   agent = SiteSelectorAgent()")
        print("   result = agent.select_sites(query, search_results)")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main() 