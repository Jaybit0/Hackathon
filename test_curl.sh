#!/bin/bash

echo "🧪 Testing MCP Search Endpoint"
echo "================================"

# Test 1: Basic search
echo "📋 Test 1: Basic search for 'OpenAI GPT-4'"
curl -X POST http://localhost:8000/mcp/tools/search_web \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "search_web",
      "arguments": {
        "query": "OpenAI GPT-4",
        "num_results": 3
      }
    }
  }'

echo -e "\n\n"

# Test 2: Search with different query
echo "📋 Test 2: Search for 'Python programming'"
curl -X POST http://localhost:8000/mcp/tools/search_web \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "search_web",
      "arguments": {
        "query": "Python programming",
        "num_results": 2
      }
    }
  }'

echo -e "\n\n"

# Test 3: Health check
echo "📋 Test 3: Health check"
curl http://localhost:8000/health

echo -e "\n\n"

# Test 4: Log statistics
echo "📋 Test 4: Log statistics"
curl http://localhost:8000/logs/stats

echo -e "\n\n✅ All tests completed!"
echo "📊 Check the logs with: python view_logs.py --tail" 