#!/bin/bash

# OpenAI MCP Integration Startup Script
# This script starts the MCP server and provides options for using OpenAI with MCP

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        echo "Please create a .env file with your API keys:"
        echo "OPENAI_API_KEY=your-openai-api-key-here"
        echo "GOOGLE_API_KEY=your-google-api-key-here"
        echo "GOOGLE_CSE_ID=your-google-cse-id-here"
        echo ""
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_status "Found .env file"
    fi
}

# Check if required Python packages are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if conda environment exists
    if conda env list | grep -q "hackathon"; then
        print_status "Found conda environment 'hackathon'"
        
        # Activate conda environment
        print_status "Activating conda environment 'hackathon'..."
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate hackathon
        
        # Check if required packages are installed
        python -c "import requests, fastapi, uvicorn, dotenv" 2>/dev/null || {
            print_warning "Some required packages are missing in conda environment."
            echo "Installing required packages in conda environment..."
            pip install requests fastapi uvicorn python-dotenv
        }
    else
        print_warning "Conda environment 'hackathon' not found!"
        echo "Please create the conda environment first:"
        echo "conda create -n hackathon python=3.9"
        echo "conda activate hackathon"
        echo "pip install requests fastapi uvicorn python-dotenv"
        echo ""
        read -p "Do you want to continue with system Python? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        
        # Check if required packages are installed
        python3 -c "import requests, fastapi, uvicorn, dotenv" 2>/dev/null || {
            print_warning "Some required packages are missing."
            echo "Installing required packages..."
            pip3 install requests fastapi uvicorn python-dotenv
        }
    fi
    
    print_status "Dependencies check complete"
}

# Start the MCP server
start_mcp_server() {
    print_header "🚀 Starting MCP Server..."
    
    # Check if server is already running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "MCP server is already running on http://localhost:8000"
        return 0
    fi
    
    print_status "Starting enhanced search server..."
    
    # Start the server in the background
    nohup uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload > mcp_server.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    print_status "Waiting for server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_status "✅ MCP server started successfully!"
            print_status "Server PID: $SERVER_PID"
            print_status "Logs: mcp_server.log"
            return 0
        fi
        sleep 1
    done
    
    print_error "Failed to start MCP server"
    return 1
}

# Test the MCP server
test_mcp_server() {
    print_header "🧪 Testing MCP Server..."
    
    # Test basic connectivity
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "✅ Server is responding"
    else
        print_error "❌ Server is not responding"
        return 1
    fi
    
    # Test search functionality
    print_status "Testing search functionality..."
    if conda env list | grep -q "hackathon"; then
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate hackathon
        python test_mcp_client.py > /dev/null 2>&1
    else
        python3 test_mcp_client.py > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        print_status "✅ Search functionality working"
    else
        print_warning "⚠️  Search functionality may have issues"
    fi
}

# Show usage options
show_usage_options() {
    print_header "🎯 Usage Options"
    echo ""
    if conda env list | grep -q "hackathon"; then
        echo "1. Interactive Chat (Recommended)"
        echo "   conda activate hackathon && python interactive_mcp_client.py"
        echo ""
        echo "2. Test MCP Server"
        echo "   conda activate hackathon && python test_mcp_client.py"
        echo ""
        echo "3. View Logs"
        echo "   conda activate hackathon && python view_logs.py --tail"
        echo ""
        echo "4. Programmatic Usage"
        echo "   conda activate hackathon && python openai_client_with_mcp.py"
    else
        echo "1. Interactive Chat (Recommended)"
        echo "   python3 interactive_mcp_client.py"
        echo ""
        echo "2. Test MCP Server"
        echo "   python3 test_mcp_client.py"
        echo ""
        echo "3. View Logs"
        echo "   python3 view_logs.py --tail"
        echo ""
        echo "4. Programmatic Usage"
        echo "   python3 openai_client_with_mcp.py"
    fi
    echo ""
    echo "5. Check Server Status"
    echo "   curl http://localhost:8000/health"
    echo ""
}

# Main function
main() {
    print_header "🤖 OpenAI MCP Integration Startup"
    echo "=========================================="
    
    # Check environment
    check_env
    
    # Check dependencies
    check_dependencies
    
    # Start MCP server
    if start_mcp_server; then
        # Test the server
        test_mcp_server
        
        echo ""
        print_header "🎉 Setup Complete!"
        echo ""
        show_usage_options
        
        echo ""
        print_status "Ready to use OpenAI with MCP integration!"
        echo ""
        echo "💡 Quick start: python3 interactive_mcp_client.py"
        echo ""
        
        # Ask if user wants to start interactive mode
        read -p "Would you like to start interactive chat now? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            if conda env list | grep -q "hackathon"; then
                echo "You can start interactive chat later with: conda activate hackathon && python interactive_mcp_client.py"
            else
                echo "You can start interactive chat later with: python3 interactive_mcp_client.py"
            fi
        else
            echo "Starting interactive chat..."
            if conda env list | grep -q "hackathon"; then
                source $(conda info --base)/etc/profile.d/conda.sh
                conda activate hackathon
                python interactive_mcp_client.py
            else
                python3 interactive_mcp_client.py
            fi
        fi
    else
        print_error "Failed to start MCP server. Check the logs for details."
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "stop")
        print_status "Stopping MCP server..."
        pkill -f "uvicorn enhanced_search_server:app" || true
        print_status "MCP server stopped"
        ;;
    "restart")
        print_status "Restarting MCP server..."
        pkill -f "uvicorn enhanced_search_server:app" || true
        sleep 2
        main
        ;;
    "status")
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_status "✅ MCP server is running"
            curl -s http://localhost:8000/health | python3 -m json.tool
        else
            print_error "❌ MCP server is not running"
        fi
        ;;
    "logs")
        if [ -f "mcp_server.log" ]; then
            tail -f mcp_server.log
        else
            print_error "No server log file found"
        fi
        ;;
    "test")
        test_mcp_server
        ;;
    "help"|"-h"|"--help")
        echo "OpenAI MCP Integration Startup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Start MCP server and show usage options"
        echo "  stop       Stop the MCP server"
        echo "  restart    Restart the MCP server"
        echo "  status     Check server status"
        echo "  logs       Show server logs"
        echo "  test       Test MCP server functionality"
        echo "  help       Show this help message"
        echo ""
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac 