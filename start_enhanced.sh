#!/bin/bash

echo "🚀 Starting Enhanced Search Server with Result Enhancement..."
echo "=" * 60

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your Google API credentials:"
    echo "GOOGLE_API_KEY=your_api_key_here"
    echo "GOOGLE_CSE_ID=your_cse_id_here"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import fastapi, requests, python-dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip install fastapi uvicorn requests python-dotenv
fi

# Create logs directory if it doesn't exist
mkdir -p mcp_logs

echo "🎯 Enhanced Features:"
echo "   • Custom entries based on keywords"
echo "   • Configurable result enhancement"
echo "   • MCP traffic logging"
echo "   • Real-time result modification"
echo ""

echo "🔗 Server will be available at: http://localhost:8000"
echo "📊 Logs will be saved to: mcp_logs/"
echo "🎯 Custom entries will be added to search results"
echo ""

# Start the enhanced server
echo "🚀 Starting server..."
uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload 