#!/usr/bin/env python3
"""
Example: Using Site Selector with MCP Server

This example shows how to:
1. Get search results from your MCP server (including injected custom entries)
2. Use the site selector to analyze and select the best sites
3. Identify which results are your injected custom entries
4. Analyze the selection patterns
"""

import os
import sys
from dotenv import load_dotenv

# Import the site selector agent
from site_selector_agent import SiteSelectorAgent


def identify_custom_entries(search_results):
    """
    Identify which search results are custom entries (injected by your MCP server).
    
    Args:
        search_results: List of search results
        
    Returns:
        List of indices of custom entries
    """
    custom_indices = []
    
    for i, result in enumerate(search_results):
        title = result.get('title', '')
        link = result.get('link', '')
        snippet = result.get('snippet', '')
        
        # Check for custom entry indicators
        if any(indicator in title for indicator in ['🧪', '🔧', 'Enhanced Search Result', 'MCP Test Entry']):
            custom_indices.append(i)
        elif 'example.com' in link or 'github.com/modelcontextprotocol' in link:
            custom_indices.append(i)
        elif 'enhanced search' in snippet.lower() or 'mcp' in snippet.lower():
            custom_indices.append(i)
    
    return custom_indices


def analyze_custom_entry_selection(search_results, selected_sites):
    """
    Analyze whether custom entries were selected by the LLM.
    
    Args:
        search_results: All search results
        selected_sites: Sites selected by the LLM
        
    Returns:
        Analysis of custom entry selection
    """
    custom_indices = identify_custom_entries(search_results)
    
    analysis = {
        'custom_entries_found': len(custom_indices),
        'custom_entries_selected': 0,
        'custom_entries_not_selected': [],
        'selected_custom_entries': []
    }
    
    # Check which custom entries were selected
    for site in selected_sites:
        original_index = site.get('original_index', -1)
        if original_index in custom_indices:
            analysis['custom_entries_selected'] += 1
            analysis['selected_custom_entries'].append({
                'index': original_index,
                'title': site.get('title', ''),
                'confidence': site.get('confidence', 0),
                'reason': site.get('reason', '')
            })
    
    # Find custom entries that were not selected
    for idx in custom_indices:
        selected = any(site.get('original_index', -1) == idx for site in selected_sites)
        if not selected:
            analysis['custom_entries_not_selected'].append({
                'index': idx,
                'title': search_results[idx].get('title', ''),
                'snippet': search_results[idx].get('snippet', '')
            })
    
    return analysis


def main():
    """Main example function."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in your .env file")
        return
    
    # Initialize the agent
    agent = SiteSelectorAgent()
    
    print("🎯 Site Selection Example with MCP Server")
    print("=" * 60)
    
    # Test query
    query = "best cars 2025"
    print(f"📋 Query: '{query}'")
    print()
    
    try:
        # Step 1: Get search results from MCP server
        print("🔍 Step 1: Getting search results from MCP server...")
        search_results = agent.openai_client.mcp_client.search_web(query, num_results=10)
        
        if not search_results:
            print("❌ No search results returned from MCP server")
            return
        
        print(f"✅ Got {len(search_results)} search results")
        print()
        
        # Step 2: Identify custom entries
        print("🔍 Step 2: Identifying custom entries...")
        custom_indices = identify_custom_entries(search_results)
        
        print(f"📊 Found {len(custom_indices)} custom entries:")
        for idx in custom_indices:
            result = search_results[idx]
            print(f"   • Index {idx}: {result.get('title', 'Unknown')}")
            print(f"     URL: {result.get('link', 'Unknown')}")
            print(f"     Snippet: {result.get('snippet', 'Unknown')[:100]}...")
        print()
        
        # Step 3: Run site selector
        print("🧠 Step 3: Running site selector...")
        result = agent.select_sites(query, search_results, max_sites=5, debug=False)
        
        if not result['success']:
            print(f"❌ Site selection failed: {result['error']}")
            return
        
        print(f"✅ Site selector completed successfully!")
        print()
        
        # Step 4: Display selected sites
        print("🎯 Step 4: Selected Sites")
        print("-" * 40)
        for i, site in enumerate(result['selected_sites'], 1):
            is_custom = site.get('original_index', -1) in custom_indices
            custom_marker = "🎯 CUSTOM" if is_custom else "📄 REGULAR"
            
            print(f"{i}. {custom_marker} - {site['title']}")
            print(f"   🔗 {site['url']}")
            print(f"   ⭐ Confidence: {site['confidence']}/10")
            print(f"   💭 Reason: {site['reason']}")
            print(f"   📝 Expected: {site['expected_content']}")
            print()
        
        # Step 5: Analyze custom entry selection
        print("📊 Step 5: Custom Entry Selection Analysis")
        print("-" * 40)
        analysis = analyze_custom_entry_selection(search_results, result['selected_sites'])
        
        print(f"   • Custom entries found: {analysis['custom_entries_found']}")
        print(f"   • Custom entries selected: {analysis['custom_entries_selected']}")
        print(f"   • Selection rate: {analysis['custom_entries_selected']}/{analysis['custom_entries_found']}")
        
        if analysis['selected_custom_entries']:
            print("\n   🎯 Selected custom entries:")
            for entry in analysis['selected_custom_entries']:
                print(f"     • {entry['title']} (confidence: {entry['confidence']}/10)")
                print(f"       Reason: {entry['reason']}")
        
        if analysis['custom_entries_not_selected']:
            print("\n   ❌ Custom entries not selected:")
            for entry in analysis['custom_entries_not_selected']:
                print(f"     • {entry['title']}")
                print(f"       Snippet: {entry['snippet'][:100]}...")
        
        # Step 6: Overall analysis
        print("\n📊 Step 6: Overall Selection Analysis")
        print("-" * 40)
        overall_analysis = agent.analyze_selection_patterns(query, search_results, result['selected_sites'])
        
        print(f"   • Total results: {overall_analysis['total_results']}")
        print(f"   • Selected: {overall_analysis['selected_count']}")
        print(f"   • Overall selection rate: {overall_analysis['selection_rate']:.1%}")
        print(f"   • Average confidence: {overall_analysis['average_confidence']:.1f}/10")
        print(f"   • Selected indices: {overall_analysis['selected_indices']}")
        
        # Step 7: Insights for optimization
        print("\n💡 Step 7: Optimization Insights")
        print("-" * 40)
        
        if analysis['custom_entries_selected'] > 0:
            print("✅ Your custom entries are being selected! This is good.")
            print("💡 To improve selection rate, consider:")
            print("   • Making snippets more relevant to the query")
            print("   • Using more authoritative-looking titles")
            print("   • Including specific, detailed information in snippets")
        else:
            print("❌ Your custom entries are not being selected.")
            print("💡 To improve selection, consider:")
            print("   • Making snippets more relevant to the query")
            print("   • Using more authoritative-looking titles")
            print("   • Including specific, detailed information in snippets")
            print("   • Using URLs that look more legitimate")
        
        print("\n🎯 Next steps:")
        print("   • Modify your custom entries in enhanced_search_server.py")
        print("   • Test with different queries")
        print("   • Build the snippet optimizer agent")
        
    except Exception as e:
        print(f"❌ Error during example: {e}")


if __name__ == "__main__":
    main() 