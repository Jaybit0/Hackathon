# OpenAI API Client

A comprehensive Python script for querying OpenAI models. Supports chat completions, text completions, and embeddings.

## Features

- ✅ Chat completions (GPT-3.5, GPT-4, etc.)
- ✅ Text completions (legacy API)
- ✅ Embeddings generation
- ✅ Model listing
- ✅ Error handling
- ✅ Environment variable support
- ✅ Type hints
- ✅ Comprehensive examples

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key (choose one method):**
   
   **Option A: Environment variable**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
   
   **Option B: .env file**
   Create a `.env` file in the same directory:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## Usage

### Run the example script:
```bash
python openai_client.py
```

### Use as a module:

```python
from openai_client import OpenAIClient

# Initialize client
client = OpenAIClient()

# Chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
]
response = client.chat_completion(messages, model="gpt-4o")
print(response['choices'][0]['message']['content'])

# Text completion
prompt = "The quick brown fox jumps over the lazy dog. This sentence contains"
response = client.text_completion(prompt, model="gpt-4o")
print(response['choices'][0]['message']['content'])

# Embeddings
text = "Hello, world!"
response = client.create_embedding(text)
embedding = response['data'][0]['embedding']
print(f"Embedding dimensions: {len(embedding)}")

# List models
models_response = client.list_models()
for model in models_response['data']:
    print(model['id'])
```

## API Methods

### `OpenAIClient(api_key=None, base_url="https://api.openai.com/v1")`
Initialize the client. If no API key is provided, it will look for the `OPENAI_API_KEY` environment variable.

### `chat_completion(messages, model="gpt-4o", temperature=0.7, max_tokens=None, stream=False)`
Create a chat completion using the chat completions API.

**Parameters:**
- `messages`: List of message dictionaries with 'role' and 'content'
- `model`: Model to use (e.g., "gpt-4o", "gpt-4", "gpt-3.5-turbo")
- `temperature`: Controls randomness (0-2)
- `max_tokens`: Maximum tokens to generate
- `stream`: Whether to stream the response

### `text_completion(prompt, model="gpt-4o", temperature=0.7, max_tokens=None)`
Create a text completion using the chat completions API with a single user message.

**Parameters:**
- `prompt`: Text prompt
- `model`: Model to use
- `temperature`: Controls randomness (0-2)
- `max_tokens`: Maximum tokens to generate

### `create_embedding(text, model="text-embedding-ada-002")`
Create embeddings for text.

**Parameters:**
- `text`: Text or list of texts to embed
- `model`: Embedding model to use

### `list_models()`
List all available models.

## Error Handling

The script includes comprehensive error handling:

- `OpenAIError`: Custom exception for API-related errors
- Network timeout handling
- JSON parsing error handling
- API key validation

## Examples

The script includes several examples when run directly:

1. **Chat Completion**: Basic conversation with GPT-3.5-turbo
2. **Text Completion**: Legacy API usage with text-davinci-003
3. **Embeddings**: Creating embeddings for text
4. **Model Listing**: Displaying available models grouped by type

## Environment Variables

The script supports multiple ways to set your OpenAI API key:

1. **Environment variable**: `export OPENAI_API_KEY='your-api-key-here'`
2. **.env file**: Create a `.env` file with `OPENAI_API_KEY=your-api-key-here`
3. **Direct parameter**: Pass `api_key='your-api-key-here'` to `OpenAIClient()`

### .env File Format
Create a `.env` file in the same directory as the script:
```
OPENAI_API_KEY=your-openai-api-key-here
```

## Dependencies

- `requests`: HTTP library for API calls
- `python-dotenv`: For loading environment variables from .env files
- Python 3.6+

## License

This script is provided as-is for educational and development purposes. 