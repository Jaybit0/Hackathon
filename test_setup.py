#!/usr/bin/env python3
"""
Setup Test Script

This script tests that all components are properly installed and configured.
"""

import sys
import os
import importlib
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn", 
        "requests",
        "dotenv",
        "starlette"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {failed_imports}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful!")
    return True


def test_env_file():
    """Test that .env file exists and has required variables."""
    print("\n🔍 Testing .env file...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Create a .env file with:")
        print("GOOGLE_API_KEY=your-google-api-key")
        print("GOOGLE_CSE_ID=your-google-cse-id")
        return False
    
    print("✅ .env file found")
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["GOOGLE_API_KEY", "GOOGLE_CSE_ID"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    
    print("✅ All required environment variables found")
    return True


def test_server_startup():
    """Test that the server can be imported."""
    print("\n🔍 Testing server startup...")
    
    try:
        # Test importing the server modules
        import mcp_logger
        print("✅ mcp_logger imported successfully")
        
        import search_server_with_logging
        print("✅ search_server_with_logging imported successfully")
        
        # Test that the app can be created
        app = search_server_with_logging.app
        print("✅ FastAPI app created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False


def test_log_directory():
    """Test that log directory can be created."""
    print("\n🔍 Testing log directory...")
    
    log_dir = Path("mcp_logs")
    try:
        log_dir.mkdir(exist_ok=True)
        print("✅ Log directory created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create log directory: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 MCP Logging Setup Test")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_env_file),
        ("Server", test_server_startup),
        ("Log Directory", test_log_directory)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! You're ready to test MCP logging.")
        print("\n🚀 Next steps:")
        print("1. Start the server: ./start_with_logging.sh")
        print("2. Run test client: python test_mcp_client.py")
        print("3. View logs: python view_logs.py --tail")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main() 