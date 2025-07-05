#!/usr/bin/env python3
"""
Interactive Intelligent Search Tool

This provides an interactive interface for the intelligent search tool,
allowing users to see how the LLM decides which sites to visit.
"""

import os
import json
import sys
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Import our intelligent search tool
from intelligent_search_tool import IntelligentSearchTool


class InteractiveIntelligentSearch:
    """Interactive interface for intelligent search."""
    
    def __init__(self):
        """Initialize the interactive search interface."""
        load_dotenv()
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY not found!")
            print("Please set your OpenAI API key in your .env file")
            sys.exit(1)
        
        # Initialize the intelligent search tool
        self.tool = IntelligentSearchTool()
        
        # Conversation history
        self.search_history = []
    
    def run_interactive(self):
        """Run the interactive search interface."""
        print("🧠 Interactive Intelligent Search Tool")
        print("=" * 60)
        print("This tool lets you see how the LLM decides which websites to visit")
        print("for deeper content extraction and research.")
        print()
        print("💡 Commands:")
        print("   • Type your search query to start intelligent search")
        print("   • Type '/history' to see search history")
        print("   • Type '/clear' to clear history")
        print("   • Type '/help' to see this help message")
        print("   • Type '/quit' or '/exit' to exit")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n🔍 Enter your search query: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if user_input in ['/quit', '/exit']:
                        print("👋 Goodbye!")
                        break
                    elif user_input == '/help':
                        self.show_help()
                        continue
                    elif user_input == '/history':
                        self.show_history()
                        continue
                    elif user_input == '/clear':
                        self.search_history = []
                        print("🗑️  Search history cleared!")
                        continue
                    else:
                        print("❌ Unknown command. Type /help for available commands.")
                        continue
                
                # Perform intelligent search
                print(f"\n🚀 Starting intelligent search for: '{user_input}'")
                print("=" * 60)
                
                results = self.tool.intelligent_search(user_input, max_sites=5)
                
                if results.get('success'):
                    # Display results
                    self.display_results(results)
                    
                    # Add to history
                    self.search_history.append({
                        'query': user_input,
                        'timestamp': time.time(),
                        'results': results
                    })
                else:
                    print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def display_results(self, results: Dict[str, Any]):
        """Display intelligent search results."""
        
        # Show initial search results
        print("\n📋 INITIAL SEARCH RESULTS:")
        print("-" * 40)
        initial_results = results.get('initial_results', [])
        for i, result in enumerate(initial_results, 1):
            if "error" in result:
                continue
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No snippet")
            
            print(f"{i}. 📄 {title}")
            print(f"   🔗 {link}")
            print(f"   📝 {snippet[:100]}{'...' if len(snippet) > 100 else ''}")
        
        # Show LLM's site selection
        print("\n🧠 LLM SITE SELECTION:")
        print("-" * 40)
        selected_sites = results.get('selected_sites', [])
        for i, site in enumerate(selected_sites, 1):
            url = site.get('url', 'Unknown URL')
            title = site.get('title', 'Unknown Title')
            confidence = site.get('confidence', 0)
            reason = site.get('reason', 'No reason provided')
            
            print(f"{i}. 🎯 {title}")
            print(f"   🔗 {url}")
            print(f"   ⭐ Confidence: {confidence}/10")
            print(f"   💭 Reason: {reason}")
        
        # Show content extraction results
        print("\n📄 CONTENT EXTRACTION RESULTS:")
        print("-" * 40)
        extracted_content = results.get('extracted_content', [])
        successful_extractions = 0
        for i, content in enumerate(extracted_content, 1):
            url = content.get('url', 'Unknown URL')
            title = content.get('title', 'Unknown Title')
            confidence = content.get('confidence', 0)
            extraction_success = content.get('extraction_success', False)
            content_length = len(content.get('content', ''))
            
            status = "✅ Success" if extraction_success else "❌ Failed"
            print(f"{i}. {status} - {title}")
            print(f"   🔗 {url}")
            print(f"   ⭐ Confidence: {confidence}/10")
            print(f"   📏 Content length: {content_length} characters")
            
            if extraction_success:
                successful_extractions += 1
        
        # Show optimized summary
        print("\n📝 OPTIMIZED SUMMARY:")
        print("=" * 60)
        summary = results.get('summary', 'No summary available')
        print(summary)
        
        # Show statistics
        print("\n📊 SEARCH STATISTICS:")
        print("-" * 40)
        print(f"   • Initial search results: {len(initial_results)}")
        print(f"   • Sites selected by LLM: {len(selected_sites)}")
        print(f"   • Content extraction attempts: {len(extracted_content)}")
        print(f"   • Successful extractions: {successful_extractions}")
        print(f"   • Average confidence score: {sum(s.get('confidence', 0) for s in selected_sites) / len(selected_sites) if selected_sites else 0:.1f}/10")
    
    def show_help(self):
        """Show help information."""
        print("\n💡 HELP - Interactive Intelligent Search Tool")
        print("=" * 50)
        print()
        print("This tool performs intelligent web search with LLM-guided site selection:")
        print()
        print("1. 🔍 Initial Search")
        print("   • Performs web search using your MCP server")
        print("   • Gets multiple search results")
        print()
        print("2. 🧠 LLM Analysis")
        print("   • LLM analyzes search results")
        print("   • Decides which sites are most valuable")
        print("   • Provides confidence scores and reasons")
        print()
        print("3. 📄 Content Extraction")
        print("   • Visits selected websites")
        print("   • Extracts detailed content")
        print("   • Handles various website structures")
        print()
        print("4. 📝 Optimized Summary")
        print("   • LLM creates comprehensive summary")
        print("   • Synthesizes information from multiple sources")
        print("   • Provides well-structured, detailed answers")
        print()
        print("Commands:")
        print("   /help     - Show this help message")
        print("   /history  - Show search history")
        print("   /clear    - Clear search history")
        print("   /quit     - Exit the program")
        print()
    
    def show_history(self):
        """Show search history."""
        if not self.search_history:
            print("📚 No search history yet.")
            return
        
        print("\n📚 SEARCH HISTORY:")
        print("=" * 50)
        
        for i, entry in enumerate(self.search_history, 1):
            query = entry.get('query', 'Unknown query')
            timestamp = entry.get('timestamp', 0)
            results = entry.get('results', {})
            
            # Format timestamp
            import time
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{i}. 📋 {query}")
            print(f"   ⏰ {time_str}")
            
            if results.get('success'):
                initial_count = len(results.get('initial_results', []))
                selected_count = len(results.get('selected_sites', []))
                extracted_count = len([c for c in results.get('extracted_content', []) if c.get('extraction_success')])
                
                print(f"   📊 {initial_count} initial results → {selected_count} selected → {extracted_count} extracted")
            else:
                print(f"   ❌ Failed: {results.get('error', 'Unknown error')}")
            print()


def main():
    """Main function."""
    print("🚀 Starting Interactive Intelligent Search Tool...")
    
    # Initialize and run
    interface = InteractiveIntelligentSearch()
    interface.run_interactive()


if __name__ == "__main__":
    main() 