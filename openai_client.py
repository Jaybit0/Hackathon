#!/usr/bin/env python3
"""
OpenAI API Client

A comprehensive Python script for querying OpenAI models.
Supports chat completions, text completions, and embeddings.
"""

import os
import json
import sys
from typing import Dict, List, Optional, Union
import requests
from datetime import datetime
from dotenv import load_dotenv



class OpenAIError(Exception):
    """Custom exception for OpenAI API errors."""
    pass


class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from OPENAI_API_KEY env var or .env file.
            base_url: Base URL for the OpenAI API.
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
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict:
        """
        Create a chat completion.
        
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
        print("3. Pass directly to OpenAIClient(api_key='your-api-key-here')")
        sys.exit(1)
    
    try:
        # Initialize client
        client = OpenAIClient()
        
        print("🤖 OpenAI API Client")
        print("=" * 50)
        
        # Example 1: Chat completion
        print("\n1. Chat Completion Example:")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the capital of France?"}
        ]
        
        response = client.chat_completion(messages, model="gpt-4o", temperature=0.7)
        print(f"Response: {response['choices'][0]['message']['content']}")
        
        # Example 2: Text completion
        print("\n2. Text Completion Example:")
        prompt = "The quick brown fox jumps over the lazy dog. This sentence contains"
        
        response = client.text_completion(prompt, model="gpt-4o", max_tokens=50)
        print(f"Response: {response['choices'][0]['message']['content']}")
        
        # Example 3: Embeddings
        print("\n3. Embeddings Example:")
        text = "Hello, world!"
        
        response = client.create_embedding(text)
        embedding = response['data'][0]['embedding']
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        # Example 4: List available models
        print("\n4. Available Models:")
        models_response = client.list_models()
        models = models_response['data']
        
        # Group models by type
        model_types = {}
        for model in models:
            model_type = model['id'].split('-')[0] if '-' in model['id'] else 'other'
            if model_type not in model_types:
                model_types[model_type] = []
            model_types[model_type].append(model['id'])
        
        for model_type, model_list in model_types.items():
            print(f"\n{model_type.upper()} Models:")
            for model_id in model_list[:5]:  # Show first 5 of each type
                print(f"  - {model_id}")
            if len(model_list) > 5:
                print(f"  ... and {len(model_list) - 5} more")
        
        print("\n✅ All examples completed successfully!")
        
    except OpenAIError as e:
        print(f"❌ OpenAI Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 