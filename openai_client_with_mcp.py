#!/usr/bin/env python3
"""
OpenAI API Client with MCP Integration

This enhanced client allows OpenAI models to use your local MCP server
for web search capabilities. The LLM can now search the web through
your local MCP server.
"""

import os
import json
import sys
import requests
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dotenv import load_dotenv


class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass


class MCPError(Exception):
    """Custom exception for MCP server errors."""
    pass


class MCPClient:
    """Client for interacting with the local MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server
        """
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
            response = self.session.post(
                f"{self.base_url}/mcp/tools/{tool_name}",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the actual result from MCP response
            if "result" in result and "content" in result["result"]:
                content = result["result"]["content"]
                if content and len(content) > 0 and "text" in content[0]:
                    # Parse the JSON text back to a dictionary
                    return json.loads(content[0]["text"])
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise MCPError(f"MCP request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise MCPError(f"Failed to parse MCP response: {str(e)}")
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using the MCP server.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        return self.call_tool("search_web", {
            "query": query,
            "num_results": num_results
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools."""
        try:
            response = self.session.get(f"{self.base_url}/mcp/tools")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise MCPError(f"Failed to list tools: {str(e)}")


class OpenAIClientWithMCP:
    """Enhanced OpenAI client with MCP integration."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1", mcp_url: str = "http://localhost:8000"):
        """
        Initialize the OpenAI client with MCP integration.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from OPENAI_API_KEY env var or .env file.
            base_url: Base URL for the OpenAI API.
            mcp_url: Base URL for the MCP server.
        """
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable, .env file, or pass api_key parameter.")
        
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize MCP client
        self.mcp_client = MCPClient(mcp_url)
    
    def _make_request(self, endpoint: str, data: Dict) -> Dict:
        """
        Make a request to the OpenAI API.
        
        Args:
            endpoint: API endpoint (e.g., "/chat/completions")
            data: Request data
            
        Returns:
            API response as dictionary
            
        Raises:
            OpenAIError: If the API request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise OpenAIError(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise OpenAIError(f"Failed to parse API response: {str(e)}")
    
    def chat_completion_with_search(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        enable_search: bool = True,
        search_queries: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a chat completion with optional web search integration.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use for completion
            temperature: Controls randomness (0-2)
            max_tokens: Maximum tokens to generate
            enable_search: Whether to enable web search for relevant queries
            search_queries: Optional list of search queries to perform
            
        Returns:
            API response dictionary with search results included
        """
        # If search is enabled, perform web searches
        search_results = []
        if enable_search:
            if search_queries:
                # Use provided search queries
                for query in search_queries:
                    try:
                        results = self.mcp_client.search_web(query, num_results=3)
                        search_results.extend(results)
                        print(f"🔍 Searched for '{query}': Found {len(results)} results")
                    except MCPError as e:
                        print(f"⚠️  Search failed for '{query}': {e}")
            else:
                # Extract potential search queries from the conversation
                search_queries = self._extract_search_queries(messages)
                for query in search_queries:
                    try:
                        results = self.mcp_client.search_web(query, num_results=3)
                        search_results.extend(results)
                        print(f"🔍 Searched for '{query}': Found {len(results)} results")
                    except MCPError as e:
                        print(f"⚠️  Search failed for '{query}': {e}")
        
        # Add search results to the conversation if any were found
        if search_results:
            search_context = self._format_search_results(search_results)
            # Add search context as a system message
            enhanced_messages = [
                {"role": "system", "content": f"You have access to the following web search results. Use them to provide accurate and up-to-date information:\n\n{search_context}"}
            ] + messages
        else:
            enhanced_messages = messages
        
        # Make the API call
        data = {
            "model": model,
            "messages": enhanced_messages,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        return self._make_request("/chat/completions", data)
    
    def _extract_search_queries(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        Extract potential search queries from conversation messages.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            List of potential search queries
        """
        queries = []
        
        # Look for user messages that might benefit from web search
        for message in messages:
            if message.get("role") == "user":
                content = message.get("content", "")
                
                # Simple heuristics for identifying search-worthy queries
                if any(keyword in content.lower() for keyword in [
                    "latest", "recent", "current", "today", "news", "update",
                    "what is", "how to", "where", "when", "who", "why",
                    "search", "find", "look up", "information about"
                ]):
                    # Extract a search query (simplified)
                    words = content.split()
                    if len(words) > 2:
                        # Take first few meaningful words as search query
                        query = " ".join(words[:5])
                        queries.append(query)
        
        return queries[:3]  # Limit to 3 searches
    
    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results for inclusion in the conversation.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted search results as string
        """
        if not results:
            return "No search results found."
        
        formatted = "Web Search Results:\n\n"
        
        for i, result in enumerate(results, 1):
            if "error" in result:
                continue
                
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No snippet")
            
            formatted += f"{i}. {title}\n"
            formatted += f"   URL: {link}\n"
            formatted += f"   {snippet}\n\n"
        
        return formatted
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict:
        """
        Create a chat completion (original method without search).
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use for completion
            temperature: Controls randomness (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            API response dictionary
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        return self._make_request("/chat/completions", data)
    
    def text_completion(
        self,
        prompt: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict:
        """
        Create a text completion using the chat completions API with a single user message.
        
        Args:
            prompt: Text prompt
            model: Model to use (defaults to gpt-4o)
            temperature: Controls randomness (0-2)
            max_tokens: Maximum tokens to generate
            
        Returns:
            API response dictionary
        """
        # Convert to chat completion format for better compatibility
        messages = [{"role": "user", "content": prompt}]
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        return self._make_request("/chat/completions", data)
    
    def create_embedding(
        self,
        text: Union[str, List[str]],
        model: str = "text-embedding-ada-002"
    ) -> Dict:
        """
        Create embeddings for text.
        
        Args:
            text: Text or list of texts to embed
            model: Embedding model to use
            
        Returns:
            API response dictionary
        """
        if isinstance(text, str):
            text = [text]
        
        data = {
            "model": model,
            "input": text
        }
        
        return self._make_request("/embeddings", data)
    
    def list_models(self) -> Dict:
        """
        List available models.
        
        Returns:
            API response dictionary
        """
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise OpenAIError(f"Failed to list models: {str(e)}")
    
    def test_mcp_connection(self) -> bool:
        """
        Test the connection to the MCP server.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            tools = self.mcp_client.list_tools()
            print(f"✅ MCP server connection successful")
            print(f"📋 Available tools: {json.dumps(tools, indent=2)}")
            return True
        except MCPError as e:
            print(f"❌ MCP server connection failed: {e}")
            return False


def main():
    """Main function with example usage."""
    
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment variables or .env file.")
        print("Please set your OpenAI API key in one of these ways:")
        print("1. Environment variable: export OPENAI_API_KEY='your-api-key-here'")
        print("2. .env file: Create a .env file with OPENAI_API_KEY=your-api-key-here")
        print("3. Pass directly to OpenAIClientWithMCP(api_key='your-api-key-here')")
        sys.exit(1)
    
    try:
        # Initialize client
        client = OpenAIClientWithMCP()
        
        print("🤖 OpenAI API Client with MCP Integration")
        print("=" * 60)
        
        # Test MCP connection
        print("\n🔗 Testing MCP server connection...")
        if not client.test_mcp_connection():
            print("⚠️  MCP server not available. Make sure to start it with:")
            print("   uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload")
            print("   or")
            print("   ./start_enhanced.sh")
            return
        
        # Example 1: Chat completion with automatic search
        print("\n1. Chat Completion with Web Search Example:")
        messages = [
            {"role": "system", "content": "You are a helpful assistant with access to web search. Use search results to provide accurate information."},
            {"role": "user", "content": "What are the latest features of OpenAI's GPT-4?"}
        ]
        
        response = client.chat_completion_with_search(messages, model="gpt-4o", temperature=0.7)
        print(f"Response: {response['choices'][0]['message']['content']}")
        
        # Example 2: Chat completion with specific search queries
        print("\n2. Chat Completion with Specific Search Queries:")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about Python programming best practices."}
        ]
        
        response = client.chat_completion_with_search(
            messages, 
            model="gpt-4o", 
            temperature=0.7,
            search_queries=["Python programming best practices 2024", "Python coding standards"]
        )
        print(f"Response: {response['choices'][0]['message']['content']}")
        
        # Example 3: Regular chat completion (without search)
        print("\n3. Regular Chat Completion (No Search):")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2 + 2?"}
        ]
        
        response = client.chat_completion(messages, model="gpt-4o", temperature=0.7)
        print(f"Response: {response['choices'][0]['message']['content']}")
        
        print("\n✅ All examples completed successfully!")
        print("\n💡 Usage Tips:")
        print("   • Use chat_completion_with_search() for queries that need current information")
        print("   • Use chat_completion() for general conversation")
        print("   • The MCP server logs all requests - check mcp_logs/ for details")
        
    except OpenAIError as e:
        print(f"❌ OpenAI Error: {e}")
    except MCPError as e:
        print(f"❌ MCP Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


if __name__ == "__main__":
    main() 