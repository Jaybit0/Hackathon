#!/bin/bash

echo "🚀 Starting Search Server with MCP Logging..."
echo "📊 All MCP traffic will be logged to 'mcp_logs/' directory"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Make sure you have GOOGLE_API_KEY and GOOGLE_CSE_ID set."
fi

# Create logs directory if it doesn't exist
mkdir -p mcp_logs

# Start the server with logging
python -m uvicorn search_server_with_logging:app --host 0.0.0.0 --port 8000 --reload 