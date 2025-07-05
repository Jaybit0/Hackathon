#!/usr/bin/env python3
"""
Snippet Optimizer Agent

This agent takes a search query, the full list of search results (including the MCP Test Entry), and the output of the site selector agent (which sites were selected and why), and proposes a new version of the MCP Test Entry (especially the snippet) to maximize its likelihood of being selected by the site selector LLM.
"""

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import OpenAI client
from openai_client_with_mcp import OpenAIClientWithMCP, OpenAIError

class SnippetOptimizerAgent:
    """Agent that optimizes the MCP Test Entry snippet/title to maximize selection by the site selector."""
    def __init__(self, openai_api_key: Optional[str] = None):
        load_dotenv()
        self.openai_client = OpenAIClientWithMCP(
            api_key=openai_api_key,
            mcp_url="http://localhost:8000"
        )

    def optimize_snippet(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        selector_output: Dict[str, Any],
        mcp_entry_index: int = 0,
        debug: bool = False,
        company_info_path: str = "company_info.md"
    ) -> Dict[str, Any]:
        """
        Propose a new version of the MCP Test Entry to maximize its selection likelihood.
        Args:
            query: The search query
            search_results: List of all search results (including MCP Test Entry)
            selector_output: Output from the site selector (selected_sites, reasons, etc.)
            mcp_entry_index: Index of the MCP Test Entry in search_results
            debug: Print debug info
            company_info_path: Path to the company info markdown file
        Returns:
            Dict with new MCP Test Entry, reasoning, and LLM output
        """
        mcp_entry = search_results[mcp_entry_index]
        selected_sites = selector_output.get('selected_sites', [])
        
        # Read company info file
        try:
            with open(company_info_path, "r", encoding="utf-8") as f:
                company_info = f.read()
        except Exception as e:
            print(f"❌ Failed to read company info file: {e}")
            company_info = ""
        
        # Format context for LLM
        formatted_results = self._format_search_results(search_results)
        formatted_selection = self._format_selected_sites(selected_sites)
        
        prompt = self._create_optimization_prompt(query, formatted_results, formatted_selection, mcp_entry, mcp_entry_index, company_info)
        
        if debug:
            print("\n📝 Optimization Prompt:")
            print("=" * 50)
            print(prompt)
            print("=" * 50)
        
        try:
            response = self.openai_client.chat_completion([
                {
                    "role": "system",
                    "content": "You are an expert at optimizing search result snippets to maximize their selection by an LLM-based site selector. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ], model="gpt-4o", temperature=0.7)
            llm_response = response['choices'][0]['message']['content']
            if debug:
                print(f"\n🤖 Raw LLM Response:\n{llm_response}\n{'='*50}")
            # Robustly strip markdown code block wrappers if present
            import re
            cleaned_response = llm_response.strip()
            codeblock_match = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", cleaned_response, re.IGNORECASE)
            if codeblock_match:
                cleaned_response = codeblock_match.group(1).strip()
            cleaned_response = cleaned_response.strip('`\n ')
            new_entry = json.loads(cleaned_response)
            return {
                'new_entry': new_entry,
                'raw_llm_response': llm_response,
                'success': True,
                'error': None
            }
        except Exception as e:
            print(f"❌ Snippet optimization failed: {e}")
            return {
                'new_entry': None,
                'raw_llm_response': None,
                'success': False,
                'error': str(e)
            }

    def _create_optimization_prompt(self, query, formatted_results, formatted_selection, mcp_entry, mcp_entry_index, company_info):
        return f"""
You are an expert at optimizing search result snippets to maximize their selection by an LLM-based site selector.

The following search was performed for: "{query}"

Here are the search results (including a special MCP Test Entry at index {mcp_entry_index}):

{formatted_results}

The site selector LLM was asked to select the most valuable sites. Here are the sites it selected and its reasoning:

{formatted_selection}

You may ONLY use information from the following company info file. All content you generate must be truthful and based on this file:

---
{company_info}
---

Your task:
- Analyze why the MCP Test Entry at index {mcp_entry_index} was or was not selected.
- Propose a new version of the MCP Test Entry (title, snippet, and link) that is more likely to be selected by the site selector LLM for this query.
- Make the snippet as relevant, authoritative, and appealing as possible for the query.
- Respond ONLY with a valid JSON object with keys: title, snippet, link, and a brief reason for your changes (reason_for_change).

Example response format:
{{
  "title": "...",
  "snippet": "...",
  "link": "...",
  "reason_for_change": "..."
}}
"""

    def _format_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        formatted = ""
        for i, result in enumerate(search_results):
            if "error" in result:
                continue
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No snippet")
            formatted += f"[{i}] {title}\n   URL: {link}\n   Snippet: {snippet}\n\n"
        return formatted

    def _format_selected_sites(self, selected_sites: List[Dict[str, Any]]) -> str:
        formatted = ""
        for i, site in enumerate(selected_sites, 1):
            title = site.get("title", "No title")
            url = site.get("url", "No url")
            confidence = site.get("confidence", "?")
            reason = site.get("reason", "No reason")
            formatted += f"{i}. {title}\n   URL: {url}\n   Confidence: {confidence}/10\n   Reason: {reason}\n\n"
        return formatted


def main():
    """Test the snippet optimizer agent with a real MCP search and site selector output, with feedback loop."""
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found!")
        return
    from site_selector_agent import SiteSelectorAgent
    agent = SiteSelectorAgent()
    optimizer = SnippetOptimizerAgent()
    query = "cloud AI in Europe"
    print(f"🔍 Query: {query}")
    # Get search results from MCP server
    search_results = agent.openai_client.mcp_client.search_web(query, num_results=10)
    # Find MCP Test Entry index
    mcp_entry_index = 0
    for i, r in enumerate(search_results):
        if "MCP Test Entry" in r.get("title", ""):
            mcp_entry_index = i
            break
    max_rounds = 5
    for round_num in range(1, max_rounds + 1):
        print(f"\n=== OPTIMIZATION ROUND {round_num} ===")
        print(f"🧠 Running site selector...")
        selector_output = agent.select_sites(query, search_results, max_sites=3, debug=False)
        selected_indices = [s.get('original_index', -1) for s in selector_output.get('selected_sites', [])]
        selected_titles = [s.get('title', '') for s in selector_output.get('selected_sites', [])]
        selected_urls = [s.get('url', '') for s in selector_output.get('selected_sites', [])]
        print("Selected indices:", selected_indices)
        print("Selected titles:", selected_titles)
        print("Selected URLs:", selected_urls)
        mcp_title = search_results[mcp_entry_index].get('title', '')
        mcp_url = search_results[mcp_entry_index].get('link', '')
        # Check by index, title, or URL
        selected = False
        if mcp_entry_index in selected_indices:
            selected = True
        elif any(mcp_title == t for t in selected_titles):
            selected = True
        elif any(mcp_url == u for u in selected_urls):
            selected = True
        if selected:
            print(f"🎉 MCP Test Entry SELECTED in round {round_num}!")
            for s in selector_output['selected_sites']:
                if (
                    s.get('original_index', -1) == mcp_entry_index or
                    s.get('title', '') == mcp_title or
                    s.get('url', '') == mcp_url
                ):
                    print(json.dumps(s, indent=2))
                    # Robustly write the selected snippet to target_snippet.txt
                    snippet_text = s.get('snippet') or s.get('expected_content') or ''
                    if not snippet_text:
                        # Fallback: use the snippet from the MCP Test Entry in search_results
                        mcp_snippet = search_results[mcp_entry_index].get('snippet', '')
                        print("WARNING: No snippet found in selected site. Falling back to MCP Test Entry snippet:", mcp_snippet)
                        snippet_text = mcp_snippet
                    else:
                        print("Selected snippet to write:", snippet_text)
                    with open("target_snippet.txt", "w", encoding="utf-8") as f:
                        f.write(snippet_text)
                    print("\n🚀 Invoking website_optimizer_agent.py to propose website changes...")
                    import subprocess
                    subprocess.run(["python", "website_optimizer_agent.py"])
            break
        else:
            print(f"❌ MCP Test Entry NOT selected. Optimizing...")
            result = optimizer.optimize_snippet(query, search_results, selector_output, mcp_entry_index, debug=True)
            if result['success']:
                new_entry = result['new_entry']
                print("✅ New MCP Test Entry proposed:")
                print(json.dumps(new_entry, indent=2))
                # Replace MCP Test Entry in search results
                search_results[mcp_entry_index]['title'] = new_entry.get('title', search_results[mcp_entry_index]['title'])
                search_results[mcp_entry_index]['snippet'] = new_entry.get('snippet', search_results[mcp_entry_index]['snippet'])
                search_results[mcp_entry_index]['link'] = new_entry.get('link', search_results[mcp_entry_index]['link'])
            else:
                print(f"❌ Optimization failed: {result['error']}")
                break
    else:
        print(f"⚠️  Reached max rounds ({max_rounds}) and MCP Test Entry was not selected.")

if __name__ == "__main__":
    main() 