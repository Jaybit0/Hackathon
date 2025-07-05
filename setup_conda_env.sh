#!/bin/bash

# Conda Environment Setup for OpenAI MCP Integration
# This script sets up the conda environment with all necessary dependencies

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

# Check if conda is available
check_conda() {
    if ! command -v conda &> /dev/null; then
        print_error "Conda is not installed or not in PATH"
        echo "Please install conda first: https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    print_status "Conda is available"
}

# Create or update conda environment
setup_conda_env() {
    print_header "🔧 Setting up conda environment 'hackathon'"
    
    # Check if environment exists
    if conda env list | grep -q "hackathon"; then
        print_status "Conda environment 'hackathon' already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing environment..."
            conda env remove -n hackathon -y
        else
            print_status "Using existing environment"
        fi
    fi
    
    # Create environment if it doesn't exist
    if ! conda env list | grep -q "hackathon"; then
        print_status "Creating conda environment 'hackathon' with Python 3.9..."
        conda create -n hackathon python=3.9 -y
    fi
    
    # Activate environment
    print_status "Activating conda environment..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate hackathon
    
    print_status "✅ Conda environment setup complete"
}

# Install required packages
install_packages() {
    print_header "📦 Installing required packages"
    
    # Activate environment
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate hackathon
    
    # Install packages
    print_status "Installing Python packages..."
    pip install requests fastapi uvicorn python-dotenv
    
    # Verify installation
    print_status "Verifying package installation..."
    python -c "
import requests
import fastapi
import uvicorn
import dotenv
print('✅ All packages installed successfully')
"
    
    print_status "✅ Package installation complete"
}

# Create .env template
create_env_template() {
    print_header "📝 Creating .env template"
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env template..."
        cat > .env << EOF
# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Google Custom Search API (for web search)
# Get your API key from: https://console.cloud.google.com/
GOOGLE_API_KEY=your-google-api-key-here

# Google Custom Search Engine ID
# Create at: https://cse.google.com/
GOOGLE_CSE_ID=your-google-cse-id-here
EOF
        print_status "✅ Created .env template"
        print_warning "Please edit .env file with your actual API keys"
    else
        print_status "✅ .env file already exists"
    fi
}

# Test the setup
test_setup() {
    print_header "🧪 Testing setup"
    
    # Activate environment
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate hackathon
    
    # Test imports
    print_status "Testing Python imports..."
    python -c "
import requests
import fastapi
import uvicorn
import dotenv
print('✅ All imports successful')
"
    
    # Test if we can start the server
    print_status "Testing server startup..."
    timeout 10s python -c "
import uvicorn
from enhanced_search_server import app
print('✅ Server can be imported')
" || print_warning "Server import test failed (this is normal if .env is not configured)"
    
    print_status "✅ Setup test complete"
}

# Show next steps
show_next_steps() {
    print_header "🎉 Setup Complete!"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your API keys:"
    echo "   nano .env"
    echo ""
    echo "2. Start the MCP server:"
    echo "   ./start_openai_mcp.sh"
    echo ""
    echo "3. Or start manually:"
    echo "   conda activate hackathon"
    echo "   uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload"
    echo ""
    echo "4. Start interactive chat:"
    echo "   conda activate hackathon"
    echo "   python interactive_mcp_client.py"
    echo ""
    echo "5. View logs:"
    echo "   conda activate hackathon"
    echo "   python view_logs.py --tail"
    echo ""
}

# Main function
main() {
    print_header "🤖 Conda Environment Setup for OpenAI MCP Integration"
    echo "=============================================================="
    
    # Check conda
    check_conda
    
    # Setup conda environment
    setup_conda_env
    
    # Install packages
    install_packages
    
    # Create .env template
    create_env_template
    
    # Test setup
    test_setup
    
    # Show next steps
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "clean")
        print_status "Cleaning up conda environment..."
        conda env remove -n hackathon -y
        print_status "Environment removed"
        ;;
    "check")
        print_status "Checking conda environment..."
        if conda env list | grep -q "hackathon"; then
            print_status "✅ Conda environment 'hackathon' exists"
            source $(conda info --base)/etc/profile.d/conda.sh
            conda activate hackathon
            python -c "import requests, fastapi, uvicorn, dotenv; print('✅ All packages available')"
        else
            print_error "❌ Conda environment 'hackathon' does not exist"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Conda Environment Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (no args)  Set up conda environment and install packages"
        echo "  clean      Remove the conda environment"
        echo "  check      Check if environment and packages are properly set up"
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