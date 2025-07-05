#!/usr/bin/env python3
"""
Intelligent Search Tool

This tool allows the LLM to:
1. Perform an initial search
2. Analyze the results and decide which sites to visit
3. Extract deeper content from selected sites
4. Provide optimized, curated results
"""

import os
import json
import requests
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

# Import our MCP client
from openai_client_with_mcp import OpenAIClientWithMCP, OpenAIError, MCPError


class IntelligentSearchTool:
    """Intelligent search tool that lets LLM decide which sites to explore."""
    
    def __init__(self, openai_api_key: Optional[str] = None, mcp_url: str = "http://localhost:8000"):
        """
        Initialize the intelligent search tool.
        
        Args:
            openai_api_key: OpenAI API key
            mcp_url: MCP server URL
        """
        load_dotenv()
        
        # Initialize OpenAI client
        self.openai_client = OpenAIClientWithMCP(
            api_key=openai_api_key,
            mcp_url=mcp_url
        )
        
        # Headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def perform_initial_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform initial search using MCP server.
        
        Args:
            query: Search query
            num_results: Number of results to get
            
        Returns:
            List of search results
        """
        print(f"🔍 Performing initial search for: '{query}'")
        
        try:
            results = self.openai_client.mcp_client.search_web(query, num_results)
            print(f"✅ Found {len(results)} initial results")
            return results
        except MCPError as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def analyze_search_results(self, query: str, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Let the LLM analyze search results and decide which sites to visit.
        
        Args:
            query: Original search query
            search_results: List of search results
            
        Returns:
            List of selected sites to visit
        """
        print("🧠 Analyzing search results with LLM...")
        
        # Format search results for LLM
        formatted_results = self._format_results_for_llm(search_results)
        
        # Create prompt for LLM analysis
        analysis_prompt = f"""
You are an intelligent web research assistant. I have performed a search for: "{query}"

Here are the search results I found:

{formatted_results}

Your task is to analyze these results and decide which websites would be most valuable to visit for deeper content extraction. Consider:

1. **Relevance**: How well does the site match the search query?
2. **Authority**: Is this a reputable, authoritative source?
3. **Content Quality**: Does the snippet suggest high-quality, detailed content?
4. **Uniqueness**: Does this site offer unique information not found elsewhere?

For each site you want to visit, provide:
- A confidence score (1-10)
- A brief reason why this site is valuable
- What specific information you expect to find

Return your analysis as a JSON array with this structure:
[
  {{
    "url": "https://example.com",
    "title": "Site Title",
    "confidence": 8,
    "reason": "Brief explanation of why this site is valuable",
    "expected_content": "What specific information you expect to find"
  }}
]

Only include sites with confidence score >= 6. Limit to maximum 5 sites.
"""
        
        try:
            # Get LLM analysis
            response = self.openai_client.chat_completion([
                {"role": "system", "content": "You are an expert web researcher. Analyze search results and select the most valuable sites to visit. Return only valid JSON."},
                {"role": "user", "content": analysis_prompt}
            ], model="gpt-4o", temperature=0.3)
            
            # Extract LLM response
            llm_response = response['choices'][0]['message']['content']
            
            # Parse JSON response
            try:
                selected_sites = json.loads(llm_response)
                print(f"✅ LLM selected {len(selected_sites)} sites to visit")
                return selected_sites
            except json.JSONDecodeError:
                print("❌ Failed to parse LLM response as JSON")
                # Fallback: select top 3 results
                return self._fallback_site_selection(search_results[:3])
                
        except OpenAIError as e:
            print(f"❌ LLM analysis failed: {e}")
            # Fallback: select top 3 results
            return self._fallback_site_selection(search_results[:3])
    
    def extract_content_from_sites(self, selected_sites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract content from selected websites.
        
        Args:
            selected_sites: List of sites to visit
            
        Returns:
            List of extracted content
        """
        print("📄 Extracting content from selected sites...")
        
        extracted_content = []
        
        for i, site in enumerate(selected_sites, 1):
            url = site.get('url')
            title = site.get('title', 'Unknown')
            confidence = site.get('confidence', 0)
            
            print(f"  {i}. Extracting from: {title} (confidence: {confidence})")
            
            try:
                content = self._extract_site_content(url)
                if content:
                    extracted_content.append({
                        'url': url,
                        'title': title,
                        'confidence': confidence,
                        'reason': site.get('reason', ''),
                        'content': content,
                        'extraction_success': True
                    })
                    print(f"    ✅ Successfully extracted content")
                else:
                    print(f"    ❌ Failed to extract content")
                    
            except Exception as e:
                print(f"    ❌ Error extracting content: {e}")
                extracted_content.append({
                    'url': url,
                    'title': title,
                    'confidence': confidence,
                    'reason': site.get('reason', ''),
                    'content': f"Failed to extract content: {str(e)}",
                    'extraction_success': False
                })
            
            # Be respectful with requests
            time.sleep(1)
        
        return extracted_content
    
    def create_optimized_summary(self, query: str, extracted_content: List[Dict[str, Any]]) -> str:
        """
        Let the LLM create an optimized summary from extracted content.
        
        Args:
            query: Original search query
            extracted_content: List of extracted content
            
        Returns:
            Optimized summary
        """
        print("📝 Creating optimized summary...")
        
        # Format extracted content for LLM
        formatted_content = self._format_extracted_content_for_llm(extracted_content)
        
        summary_prompt = f"""
You are an expert research assistant. I have extracted detailed content from multiple websites for the query: "{query}"

Here is the extracted content:

{formatted_content}

Your task is to create a comprehensive, well-structured summary that:
1. Directly answers the original query
2. Synthesizes information from multiple sources
3. Provides specific details and examples
4. Cites sources appropriately
5. Is well-organized and easy to read

Create a detailed summary that would be valuable for someone researching this topic.
"""
        
        try:
            response = self.openai_client.chat_completion([
                {"role": "system", "content": "You are an expert research assistant. Create comprehensive, well-structured summaries from multiple sources."},
                {"role": "user", "content": summary_prompt}
            ], model="gpt-4o", temperature=0.3)
            
            return response['choices'][0]['message']['content']
            
        except OpenAIError as e:
            print(f"❌ Summary creation failed: {e}")
            return f"Failed to create summary: {str(e)}"
    
    def intelligent_search(self, query: str, max_sites: int = 5) -> Dict[str, Any]:
        """
        Perform intelligent search with LLM-guided site selection.
        
        Args:
            query: Search query
            max_sites: Maximum number of sites to visit
            
        Returns:
            Complete search results with optimized summary
        """
        print(f"🚀 Starting intelligent search for: '{query}'")
        print("=" * 60)
        
        # Step 1: Initial search
        initial_results = self.perform_initial_search(query, num_results=10)
        
        if not initial_results:
            return {
                'query': query,
                'error': 'No initial search results found',
                'summary': 'Unable to perform search due to no results.'
            }
        
        # Step 2: LLM analysis and site selection
        selected_sites = self.analyze_search_results(query, initial_results)
        
        if not selected_sites:
            return {
                'query': query,
                'error': 'No sites selected for content extraction',
                'summary': 'Unable to select sites for deeper analysis.'
            }
        
        # Limit to max_sites
        selected_sites = selected_sites[:max_sites]
        
        # Step 3: Extract content from selected sites
        extracted_content = self.extract_content_from_sites(selected_sites)
        
        # Step 4: Create optimized summary
        summary = self.create_optimized_summary(query, extracted_content)
        
        # Return complete results
        return {
            'query': query,
            'initial_results': initial_results,
            'selected_sites': selected_sites,
            'extracted_content': extracted_content,
            'summary': summary,
            'success': True
        }
    
    def _format_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM analysis."""
        formatted = ""
        for i, result in enumerate(results, 1):
            if "error" in result:
                continue
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No snippet")
            
            formatted += f"{i}. {title}\n"
            formatted += f"   URL: {link}\n"
            formatted += f"   Snippet: {snippet}\n\n"
        
        return formatted
    
    def _format_extracted_content_for_llm(self, extracted_content: List[Dict[str, Any]]) -> str:
        """Format extracted content for LLM summary."""
        formatted = ""
        for i, content in enumerate(extracted_content, 1):
            url = content.get('url', 'Unknown URL')
            title = content.get('title', 'Unknown Title')
            confidence = content.get('confidence', 0)
            reason = content.get('reason', 'No reason provided')
            extracted_text = content.get('content', 'No content extracted')
            
            formatted += f"Source {i}: {title}\n"
            formatted += f"URL: {url}\n"
            formatted += f"Confidence: {confidence}/10\n"
            formatted += f"Reason for selection: {reason}\n"
            formatted += f"Content:\n{extracted_text}\n"
            formatted += "-" * 80 + "\n\n"
        
        return formatted
    
    def _fallback_site_selection(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fallback site selection when LLM analysis fails."""
        selected = []
        for result in results:
            if "error" not in result:
                selected.append({
                    'url': result.get('link', ''),
                    'title': result.get('title', 'Unknown'),
                    'confidence': 7,
                    'reason': 'Fallback selection due to LLM analysis failure',
                    'expected_content': 'General information about the topic'
                })
        return selected
    
    def _extract_site_content(self, url: str) -> Optional[str]:
        """
        Extract content from a website.
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted text content
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text from main content areas
            content_selectors = [
                'main',
                'article',
                '.content',
                '.post-content',
                '.entry-content',
                '#content',
                'body'
            ]
            
            content_text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text(separator=' ', strip=True)
                        if len(text) > 100:  # Only use substantial content
                            content_text += text + "\n\n"
                    break
            
            # If no content found with selectors, use body
            if not content_text:
                content_text = soup.get_text(separator=' ', strip=True)
            
            # Clean up the text
            content_text = re.sub(r'\s+', ' ', content_text)  # Remove extra whitespace
            content_text = re.sub(r'\n\s*\n', '\n\n', content_text)  # Clean up line breaks
            
            # Limit content length
            if len(content_text) > 5000:
                content_text = content_text[:5000] + "..."
            
            return content_text.strip()
            
        except Exception as e:
            print(f"    ❌ Error extracting content from {url}: {e}")
            return None


def main():
    """Main function for testing the intelligent search tool."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in your .env file")
        return
    
    # Initialize the tool
    tool = IntelligentSearchTool()
    
    print("🧠 Intelligent Search Tool")
    print("=" * 50)
    print("This tool lets the LLM decide which sites to visit for deeper content extraction.")
    print()
    
    # Test queries
    test_queries = [
        "What are the latest features of OpenAI's GPT-4?",
        "How to implement machine learning in Python?",
        "Best practices for web development in 2024"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Perform intelligent search
            results = tool.intelligent_search(query, max_sites=3)
            
            if results.get('success'):
                print("\n📝 OPTIMIZED SUMMARY:")
                print("=" * 50)
                print(results['summary'])
                
                print(f"\n📊 STATISTICS:")
                print(f"   • Initial results: {len(results['initial_results'])}")
                print(f"   • Sites selected by LLM: {len(results['selected_sites'])}")
                print(f"   • Content successfully extracted: {len([c for c in results['extracted_content'] if c.get('extraction_success')])}")
                
            else:
                print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error during search: {e}")
        
        print("\n" + "=" * 50)
        
        if i < len(test_queries):
            print("⏳ Waiting 5 seconds before next test...")
            time.sleep(5)


if __name__ == "__main__":
    main() 