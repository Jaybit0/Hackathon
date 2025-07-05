# OpenAI API with Local MCP Server Integration

This guide shows you how to connect your OpenAI API LLM to your local MCP (Model Context Protocol) server for enhanced web search capabilities.

## 🚀 Quick Start

### 1. Set Up Conda Environment (Recommended)

If you're using conda, set up the environment first:

```bash
# Set up conda environment with all dependencies
./setup_conda_env.sh

# Or manually:
conda create -n hackathon python=3.9
conda activate hackathon
pip install requests fastapi uvicorn python-dotenv
```

### 2. Start Your MCP Server

Start your enhanced search server:

```bash
# Option 1: Use the conda-aware start script
./start_openai_mcp.sh

# Option 2: Start manually with conda
conda activate hackathon
uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload

# Option 3: Use the original start script
./start_enhanced.sh
```

### 2. Test the MCP Server

Verify your MCP server is running:

```bash
# Test the server
curl http://localhost:8000/health

# Test the search tool with test entries
python test_mcp_working.py

# Or test with the original client
python test_mcp_client.py
```

### 3. Use OpenAI with MCP Integration

#### Option A: Interactive Chat

```bash
# With conda environment
conda activate hackathon
python interactive_mcp_client.py

# Or without conda
python3 interactive_mcp_client.py
```

This starts an interactive chat where you can:
- Chat normally with the AI
- The AI automatically searches the web when needed
- Use `/search <query>` to search directly
- Use `/history` to see conversation history

#### Option B: Programmatic Usage

```python
from openai_client_with_mcp import OpenAIClientWithMCP

# Initialize client
client = OpenAIClientWithMCP()

# Chat with automatic web search
messages = [
    {"role": "user", "content": "What are the latest features of OpenAI's GPT-4?"}
]

response = client.chat_completion_with_search(messages, model="gpt-4o")
print(response['choices'][0]['message']['content'])
```

## 📁 Files Overview

### Core Files

- **`enhanced_search_server.py`** - Your MCP server with web search capabilities
- **`openai_client_with_mcp.py`** - Enhanced OpenAI client with MCP integration
- **`interactive_mcp_client.py`** - Interactive chat interface

### Test Files

- **`test_mcp_client.py`** - Test MCP server functionality
- **`test_working_client.py`** - Test different MCP endpoints
- **`view_logs.py`** - View MCP server logs

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```env
# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key-here

# Google Custom Search API (for web search)
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CSE_ID=your-google-cse-id-here
```

**Note**: The `setup_conda_env.sh` script will create a `.env` template for you.

### MCP Server Configuration

The MCP server runs on `http://localhost:8000` by default. You can change this in the client:

```python
client = OpenAIClientWithMCP(mcp_url="http://localhost:8000")
```

## 💡 Usage Examples

### 1. Basic Chat with Web Search

```python
from openai_client_with_mcp import OpenAIClientWithMCP

client = OpenAIClientWithMCP()

messages = [
    {"role": "user", "content": "What's the latest news about AI?"}
]

response = client.chat_completion_with_search(messages)
print(response['choices'][0]['message']['content'])
```

### 2. Chat with Specific Search Queries

```python
response = client.chat_completion_with_search(
    messages,
    search_queries=["latest AI news 2024", "artificial intelligence developments"]
)
```

### 3. Direct Web Search

```python
# Search the web directly
results = client.mcp_client.search_web("Python programming tips", num_results=5)
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['link']}")
    print(f"Snippet: {result['snippet']}")
```

### 4. Regular Chat (No Search)

```python
# Use regular chat without web search
response = client.chat_completion(messages)
```

## 🎯 Features

### Automatic Search Detection

The client automatically detects when web search might be helpful based on keywords like:
- "latest", "recent", "current", "today", "news", "update"
- "what is", "how to", "where", "when", "who", "why"
- "search", "find", "look up", "information about"

### Enhanced Results

Your MCP server adds custom entries based on keywords:
- **OpenAI queries** → Official OpenAI documentation links
- **Python queries** → Python documentation and tutorials
- **GPT queries** → GPT model information

### Test Entries

The server always includes test entries to verify the MCP tool is working:
- **🧪 MCP Test Entry** → Always appears to confirm the tool is functioning
- **Test entries appear even when Google API is not configured**
- **Test entries appear even when errors occur**

### Comprehensive Logging

All MCP requests are logged to `mcp_logs/`:
- `mcp_requests.jsonl` - All incoming requests
- `mcp_responses.jsonl` - All outgoing responses
- `mcp_tool_calls.jsonl` - Tool calls with results
- `mcp_errors.jsonl` - Error logs

## 🔍 Interactive Commands

When using the interactive client:

```
💬 You: What's the weather like today?
🤖 AI: [AI responds with web search results]

💬 You: /search Python tutorials
🔍 [Direct search results displayed]

💬 You: /history
📚 [Shows conversation history]

💬 You: /clear
🗑️  [Clears conversation history]

💬 You: /help
💡 [Shows available commands]

💬 You: /quit
👋 [Exits the program]
```

## 🧪 Testing

### Test the MCP Tool

To verify your MCP tool is working correctly:

```bash
# Test with conda environment
conda activate hackathon
python test_mcp_working.py

# Or without conda
python3 test_mcp_working.py
```

This will show you:
- ✅ Test entries with 🧪 emoji to confirm the tool is working
- 📄 Search results (if Google API is configured)
- ❌ Error messages (if any issues occur)

**Expected Output:**
```
🧪 Testing MCP Search Tool
========================================

📋 Test 1: 'test query'
------------------------------
✅ Success! Found 3 results:
  1. 📄 🧪 MCP Test Entry - Tool Working!
     🔗 https://github.com/modelcontextprotocol
     📝 This test entry confirms the MCP search tool is working for query: 'test query'...
  ✅ Test entry found: 1 test entries
```

## 🛠️ Troubleshooting

### MCP Server Not Available

```bash
# Check if server is running
curl http://localhost:8000/health

# Start the server
./start_enhanced.sh
```

### API Key Issues

```bash
# Check environment variables
echo $OPENAI_API_KEY

# Or check .env file
cat .env
```

### Search Not Working

1. Verify Google API keys are set
2. Check MCP server logs: `python view_logs.py --tail`
3. Test search directly: `python test_mcp_client.py`

### Connection Errors

```python
# Test MCP connection
client = OpenAIClientWithMCP()
if client.test_mcp_connection():
    print("✅ MCP server connected!")
else:
    print("❌ MCP server not available")
```

## 📊 Monitoring

### View Logs

```bash
# View recent logs
python view_logs.py --tail

# View statistics
python view_logs.py --stats

# View specific log files
python view_logs.py --requests
python view_logs.py --responses
python view_logs.py --errors
```

### Check Server Status

```bash
# Health check
curl http://localhost:8000/health

# View custom entries
curl http://localhost:8000/custom-entries

# View logging stats
curl http://localhost:8000/logs/stats
```

## 🎨 Customization

### Add Custom Search Entries

```bash
curl -X POST http://localhost:8000/custom-entries \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "javascript",
    "entry": {
      "title": "📚 JavaScript MDN Documentation",
      "link": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
      "snippet": "Official JavaScript documentation and tutorials."
    }
  }'
```

### Modify Search Behavior

Edit `enhanced_search_server.py` to:
- Change custom entries in `CUSTOM_ENTRIES`
- Modify search result enhancement in `enhance_search_results()`
- Add new MCP tools

## 🔗 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   OpenAI API    │    │  Your MCP Server │    │  Google Search  │
│                 │    │                  │    │                 │
│  • GPT-4o      │◄──►│  • Web Search    │◄──►│  • Custom Search│
│  • GPT-3.5-turbo│   │  • Logging       │    │  • API Results  │
│  • Embeddings  │    │  • Enhancement   │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Next Steps

1. **Add More MCP Tools**: Extend your server with additional tools like file operations, database queries, etc.

2. **Streaming Support**: Implement streaming responses for real-time chat.

3. **Multi-Model Support**: Add support for other LLM providers (Anthropic, Google, etc.).

4. **Advanced Search**: Implement semantic search, filtering, and ranking.

5. **Caching**: Add result caching to improve performance.

## 📚 Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Custom Search API](https://developers.google.com/custom-search)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Happy coding! 🎉**

Your OpenAI LLM now has the power to search the web through your local MCP server! 