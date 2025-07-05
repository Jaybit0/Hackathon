#!/usr/bin/env python3
"""
Site Selector Agent

This agent takes a search query and a list of search results (including injected custom entries),
and uses an LLM to select which sites would be most valuable to visit for deeper content extraction.

The agent is designed to work with injected custom entries that can be optimized later.
"""

import os
import json
import sys
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import re

# Import OpenAI client
from openai_client_with_mcp import OpenAIClientWithMCP, OpenAIError


class SiteSelectorAgent:
    """Agent that selects which websites to visit based on search results."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the site selector agent.
        
        Args:
            openai_api_key: OpenAI API key (optional, uses env var by default)
        """
        load_dotenv()
        
        # Initialize OpenAI client
        self.openai_client = OpenAIClientWithMCP(
            api_key=openai_api_key,
            mcp_url="http://localhost:8000"  # We'll use this for search, but agent works independently
        )
    
    def select_sites(
        self, 
        query: str, 
        search_results: List[Dict[str, Any]], 
        max_sites: int = 5,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Select which sites to visit based on search results.
        
        Args:
            query: The original search query
            search_results: List of search results, each with 'title', 'link', 'snippet'
            max_sites: Maximum number of sites to select
            debug: Whether to print debug information
            
        Returns:
            Dictionary with selection results including:
            - selected_sites: List of selected sites with confidence and reasoning
            - raw_llm_response: The raw LLM response for debugging
            - success: Whether the selection was successful
            - error: Error message if failed
        """
        print(f"🧠 Site Selector Agent analyzing {len(search_results)} search results...")
        
        # Format search results for LLM
        formatted_results = self._format_search_results(search_results)
        
        # Create the analysis prompt
        analysis_prompt = self._create_analysis_prompt(query, formatted_results, max_sites)
        
        if debug:
            print(f"\n📝 Analysis Prompt:")
            print("=" * 50)
            print(analysis_prompt)
            print("=" * 50)
        
        try:
            # Get LLM analysis
            response = self.openai_client.chat_completion([
                {
                    "role": "system", 
                    "content": "You are an expert web researcher and content curator. Your task is to analyze search results and select the most valuable websites to visit for deeper content extraction. Always respond with valid JSON only."
                },
                {
                    "role": "user", 
                    "content": analysis_prompt
                }
            ], model="gpt-4o", temperature=0.3)
            
            # Extract LLM response
            llm_response = response['choices'][0]['message']['content']
            
            if debug:
                print(f"\n🤖 Raw LLM Response:")
                print("=" * 50)
                print(llm_response)
                print("=" * 50)
            
            # Parse JSON response
            try:
                # Robustly strip markdown code block wrappers if present
                cleaned_response = llm_response.strip()
                # Remove triple backtick code blocks (with or without 'json')
                codeblock_match = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", cleaned_response, re.IGNORECASE)
                if codeblock_match:
                    cleaned_response = codeblock_match.group(1).strip()
                # Remove any leading/trailing backticks or whitespace
                cleaned_response = cleaned_response.strip('`\n ')
                
                selected_sites = json.loads(cleaned_response)
                
                # Validate the response structure
                if not isinstance(selected_sites, list):
                    raise ValueError("LLM response is not a list")
                
                # Validate each selected site
                validated_sites = []
                for site in selected_sites:
                    if isinstance(site, dict) and 'url' in site:
                        validated_sites.append({
                            'url': site.get('url', ''),
                            'title': site.get('title', 'Unknown'),
                            'confidence': site.get('confidence', 5),
                            'reason': site.get('reason', 'No reason provided'),
                            'expected_content': site.get('expected_content', 'General information'),
                            'original_index': site.get('original_index', -1)  # Index in original search results
                        })
                
                print(f"✅ Successfully selected {len(validated_sites)} sites")
                
                return {
                    'selected_sites': validated_sites,
                    'raw_llm_response': llm_response,
                    'success': True,
                    'error': None
                }
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse LLM response as JSON: {e}")
                print(f"Raw LLM response was:\n{llm_response}\n{'='*50}")
                return {
                    'selected_sites': self._fallback_selection(search_results, max_sites),
                    'raw_llm_response': llm_response,
                    'success': False,
                    'error': f"JSON parsing failed: {str(e)}"
                }
                
        except OpenAIError as e:
            print(f"❌ LLM analysis failed: {e}")
            return {
                'selected_sites': self._fallback_selection(search_results, max_sites),
                'raw_llm_response': None,
                'success': False,
                'error': f"OpenAI API error: {str(e)}"
            }
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return {
                'selected_sites': self._fallback_selection(search_results, max_sites),
                'raw_llm_response': None,
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def _create_analysis_prompt(self, query: str, formatted_results: str, max_sites: int) -> str:
        """
        Create the analysis prompt for the LLM.
        
        Args:
            query: The search query
            formatted_results: Formatted search results
            max_sites: Maximum number of sites to select
            
        Returns:
            The analysis prompt
        """
        return f"""
You are an expert web researcher. I have performed a search for: "{query}"

Here are the search results I found:

{formatted_results}

Your task is to analyze these results and select the {max_sites} most valuable websites to visit for deeper content extraction.

Consider these criteria when evaluating each site:

1. **Relevance**: How well does the site match the search query?
2. **Authority**: Is this a reputable, authoritative source?
3. **Content Quality**: Does the snippet suggest high-quality, detailed content?
4. **Uniqueness**: Does this site offer unique information not found elsewhere?
5. **Recency**: Is the information likely to be up-to-date?
6. **Depth**: Does the site likely contain comprehensive information?

For each site you select, provide:
- A confidence score (1-10, where 10 is highest confidence)
- A brief reason why this site is valuable
- What specific information you expect to find

IMPORTANT: Respond ONLY with a valid JSON array. Do not include any other text, explanations, or markdown formatting.

Example response format:
[
  {{
    "url": "https://example.com",
    "title": "Site Title",
    "confidence": 8,
    "reason": "Brief explanation of why this site is valuable",
    "expected_content": "What specific information you expect to find",
    "original_index": 2
  }}
]

Only include sites with confidence score >= 6. Limit to maximum {max_sites} sites.
"""
    
    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results for LLM analysis.
        
        Args:
            search_results: List of search results
            
        Returns:
            Formatted string for LLM
        """
        formatted = ""
        for i, result in enumerate(search_results, 1):
            if "error" in result:
                continue
                
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No snippet")
            
            formatted += f"{i}. {title}\n"
            formatted += f"   URL: {link}\n"
            formatted += f"   Snippet: {snippet}\n\n"
        
        return formatted
    
    def _fallback_selection(self, search_results: List[Dict[str, Any]], max_sites: int) -> List[Dict[str, Any]]:
        """
        Fallback selection when LLM analysis fails.
        
        Args:
            search_results: List of search results
            max_sites: Maximum number of sites to select
            
        Returns:
            List of selected sites
        """
        selected = []
        for i, result in enumerate(search_results[:max_sites]):
            if "error" not in result:
                selected.append({
                    'url': result.get('link', ''),
                    'title': result.get('title', 'Unknown'),
                    'confidence': 7,
                    'reason': 'Fallback selection due to LLM analysis failure',
                    'expected_content': 'General information about the topic',
                    'original_index': i
                })
        return selected
    
    def analyze_selection_patterns(self, query: str, search_results: List[Dict[str, Any]], selected_sites: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze patterns in the LLM's site selection.
        
        Args:
            query: The search query
            search_results: All search results
            selected_sites: Sites selected by the LLM
            
        Returns:
            Analysis of selection patterns
        """
        analysis = {
            'query': query,
            'total_results': len(search_results),
            'selected_count': len(selected_sites),
            'selection_rate': len(selected_sites) / len(search_results) if search_results else 0,
            'average_confidence': sum(s.get('confidence', 0) for s in selected_sites) / len(selected_sites) if selected_sites else 0,
            'confidence_distribution': {},
            'common_reasons': {},
            'selected_indices': [s.get('original_index', -1) for s in selected_sites]
        }
        
        # Analyze confidence distribution
        for site in selected_sites:
            confidence = site.get('confidence', 0)
            analysis['confidence_distribution'][confidence] = analysis['confidence_distribution'].get(confidence, 0) + 1
        
        # Analyze common reasons
        for site in selected_sites:
            reason = site.get('reason', '').lower()
            # Extract key phrases from reasons
            key_phrases = ['official', 'authoritative', 'comprehensive', 'detailed', 'latest', 'recent', 'expert', 'reputable']
            for phrase in key_phrases:
                if phrase in reason:
                    analysis['common_reasons'][phrase] = analysis['common_reasons'].get(phrase, 0) + 1
        
        return analysis


def main():
    """Test the site selector agent."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        print("Please set your OpenAI API key in your .env file")
        return
    
    # Initialize the agent
    agent = SiteSelectorAgent()
    
    print("🧠 Site Selector Agent Test")
    print("=" * 50)
    
    # Test with sample search results
    test_query = "best cars 2025"
    test_results = [
        {
            "title": "🧪 MCP Test Entry - Tool Working!",
            "link": "https://github.com/modelcontextprotocol",
            "snippet": "This test entry confirms the MCP search tool is working for query: 'best cars 2025'. The enhanced search server is functioning properly!"
        },
        {
            "title": "Best Cars for 2025 | U.S. News",
            "link": "https://cars.usnews.com/cars-trucks/rankings",
            "snippet": "Comprehensive rankings of the best cars for 2025, including performance, safety, and value ratings."
        },
        {
            "title": "2025 Car Reviews and Ratings | Consumer Reports",
            "link": "https://www.consumerreports.org/cars/",
            "snippet": "Expert reviews and reliability ratings for 2025 vehicles, with detailed testing and analysis."
        },
        {
            "title": "Top 10 Best Cars of 2025 - Car and Driver",
            "link": "https://www.caranddriver.com/features/",
            "snippet": "Our editors' picks for the best cars of 2025, featuring performance, luxury, and value leaders."
        },
        {
            "title": "2025 Vehicle Safety Ratings - IIHS",
            "link": "https://www.iihs.org/ratings",
            "snippet": "Official safety ratings and crash test results for 2025 vehicles from the Insurance Institute for Highway Safety."
        }
    ]
    
    print(f"📋 Testing with query: '{test_query}'")
    print(f"📊 {len(test_results)} search results provided")
    print()
    
    # Run the site selector
    result = agent.select_sites(test_query, test_results, max_sites=3, debug=True)
    
    if result['success']:
        print("✅ Site selection completed successfully!")
        print()
        
        print("🎯 SELECTED SITES:")
        print("-" * 40)
        for i, site in enumerate(result['selected_sites'], 1):
            print(f"{i}. 🎯 {site['title']}")
            print(f"   🔗 {site['url']}")
            print(f"   ⭐ Confidence: {site['confidence']}/10")
            print(f"   💭 Reason: {site['reason']}")
            print(f"   📝 Expected: {site['expected_content']}")
            print()
        
        # Analyze selection patterns
        analysis = agent.analyze_selection_patterns(test_query, test_results, result['selected_sites'])
        
        print("📊 SELECTION ANALYSIS:")
        print("-" * 40)
        print(f"   • Total results: {analysis['total_results']}")
        print(f"   • Selected: {analysis['selected_count']}")
        print(f"   • Selection rate: {analysis['selection_rate']:.1%}")
        print(f"   • Average confidence: {analysis['average_confidence']:.1f}/10")
        print(f"   • Selected indices: {analysis['selected_indices']}")
        
    else:
        print(f"❌ Site selection failed: {result['error']}")
        print(f"Raw LLM response: {result['raw_llm_response']}")


if __name__ == "__main__":
    main() 