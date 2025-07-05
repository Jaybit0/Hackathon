#!/usr/bin/env python3
"""
Interactive OpenAI Client with MCP Integration

This script provides an interactive chat interface where you can talk to
OpenAI models and they can automatically search the web using your local MCP server.
"""

import os
import json
import sys
from typing import List, Dict
from dotenv import load_dotenv

# Import our enhanced client
from openai_client_with_mcp import OpenAIClientWithMCP, OpenAIError, MCPError


class InteractiveMCPClient:
    """Interactive client for chatting with OpenAI models using MCP search."""
    
    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize the interactive client.
        
        Args:
            model: OpenAI model to use
        """
        self.model = model
        self.conversation_history = []
        self.client = None
        
        # Load environment variables
        load_dotenv()
        
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ Error: OPENAI_API_KEY not found!")
            print("Please set your OpenAI API key in your .env file or environment variables.")
            sys.exit(1)
    
    def initialize(self):
        """Initialize the client and test connections."""
        try:
            print("🚀 Initializing OpenAI Client with MCP Integration...")
            self.client = OpenAIClientWithMCP()
            
            # Test MCP connection
            print("🔗 Testing MCP server connection...")
            if not self.client.test_mcp_connection():
                print("⚠️  MCP server not available!")
                print("Please start your MCP server first:")
                print("   ./start_enhanced.sh")
                print("   or")
                print("   uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload")
                return False
            
            print("✅ All connections successful!")
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})
    
    def chat_with_search(self, user_input: str, enable_search: bool = True) -> str:
        """
        Send a message to the model with optional web search.
        
        Args:
            user_input: User's message
            enable_search: Whether to enable web search
            
        Returns:
            Model's response
        """
        # Add user message to history
        self.add_message("user", user_input)
        
        try:
            if enable_search:
                # Use search-enabled completion
                response = self.client.chat_completion_with_search(
                    self.conversation_history,
                    model=self.model,
                    temperature=0.7
                )
            else:
                # Use regular completion
                response = self.client.chat_completion(
                    self.conversation_history,
                    model=self.model,
                    temperature=0.7
                )
            
            # Extract response
            assistant_message = response['choices'][0]['message']['content']
            
            # Add assistant response to history
            self.add_message("assistant", assistant_message)
            
            return assistant_message
            
        except OpenAIError as e:
            return f"❌ OpenAI Error: {e}"
        except MCPError as e:
            return f"❌ MCP Error: {e}"
        except Exception as e:
            return f"❌ Unexpected Error: {e}"
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform a web search directly.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            results = self.client.mcp_client.search_web(query, num_results)
            return results
        except MCPError as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def print_search_results(self, results: List[Dict]):
        """Print search results in a formatted way."""
        if not results:
            print("❌ No search results found.")
            return
        
        print(f"\n🔍 Found {len(results)} search results:")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            if "error" in result:
                print(f"{i}. ❌ Error: {result['error']}")
                continue
                
            title = result.get("title", "No title")
            link = result.get("link", "No link")
            snippet = result.get("snippet", "No snippet")
            
            print(f"{i}. 📄 {title}")
            print(f"   🔗 {link}")
            print(f"   📝 {snippet}")
            print()
    
    def run_interactive(self):
        """Run the interactive chat session."""
        print(f"\n🤖 Interactive Chat with {self.model}")
        print("=" * 60)
        print("💡 Commands:")
        print("   • Type your message to chat with the AI")
        print("   • Type '/search <query>' to search the web directly")
        print("   • Type '/history' to see conversation history")
        print("   • Type '/clear' to clear conversation history")
        print("   • Type '/help' to see this help message")
        print("   • Type '/quit' or '/exit' to exit")
        print("=" * 60)
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if user_input in ['/quit', '/exit']:
                        print("👋 Goodbye!")
                        break
                    elif user_input == '/help':
                        print("\n💡 Available Commands:")
                        print("   /search <query> - Search the web directly")
                        print("   /history - Show conversation history")
                        print("   /clear - Clear conversation history")
                        print("   /help - Show this help message")
                        print("   /quit or /exit - Exit the program")
                        continue
                    elif user_input == '/history':
                        print("\n📚 Conversation History:")
                        for i, msg in enumerate(self.conversation_history, 1):
                            role = msg['role'].capitalize()
                            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                            print(f"{i}. {role}: {content}")
                        continue
                    elif user_input == '/clear':
                        self.conversation_history = []
                        print("🗑️  Conversation history cleared!")
                        continue
                    elif user_input.startswith('/search '):
                        query = user_input[8:].strip()
                        if query:
                            print(f"🔍 Searching for: {query}")
                            results = self.search_web(query, num_results=5)
                            self.print_search_results(results)
                        else:
                            print("❌ Please provide a search query: /search <query>")
                        continue
                    else:
                        print("❌ Unknown command. Type /help for available commands.")
                        continue
                
                # Regular chat
                print("🤖 AI: ", end="", flush=True)
                response = self.chat_with_search(user_input, enable_search=True)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main function."""
    print("🚀 OpenAI Interactive Chat with MCP Integration")
    print("=" * 60)
    
    # Initialize client
    client = InteractiveMCPClient()
    
    if not client.initialize():
        print("❌ Failed to initialize. Exiting.")
        return
    
    # Start interactive session
    client.run_interactive()


if __name__ == "__main__":
    main() 