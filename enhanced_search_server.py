import os
import json
import requests
from dotenv import load_dotenv
from typing import List, Dict, Any
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid

# Import our MCP logger
from mcp_logger import log_mcp_request, log_mcp_response, log_mcp_error, log_tool_call, mcp_logger

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and CSE ID from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Custom entries configuration
CUSTOM_ENTRIES = {
    "openai": [
        {
            "title": "🚀 OpenAI Official Documentation",
            "link": "https://platform.openai.com/docs",
            "snippet": "Official OpenAI API documentation and guides for developers."
        },
        {
            "title": "💡 OpenAI Community",
            "link": "https://community.openai.com/",
            "snippet": "Join the OpenAI community for discussions, tips, and support."
        }
    ],
    "gpt": [
        {
            "title": "🤖 GPT Models Overview",
            "link": "https://platform.openai.com/docs/models",
            "snippet": "Comprehensive guide to all GPT models and their capabilities."
        }
    ],
    "python": [
        {
            "title": "🐍 Python Official Documentation",
            "link": "https://docs.python.org/",
            "snippet": "Official Python documentation and tutorials."
        },
        {
            "title": "📚 Python Tutorial",
            "link": "https://docs.python.org/3/tutorial/",
            "snippet": "Learn Python programming from the official tutorial."
        }
    ]
}

# Custom middleware to capture MCP traffic
class MCPLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all MCP requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Log the incoming request
        try:
            # Read request body
            body = await request.body()
            if body:
                request_data = json.loads(body.decode())
                log_mcp_request(request_data, request_id)
        except Exception as e:
            log_mcp_error(e, {"context": "request_parsing", "request_id": request_id})
        
        # Process the request
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time
        
        # Log the response
        try:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Create new response with the same body
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            if response_body:
                response_data = json.loads(response_body.decode())
                log_mcp_response(response_data, request_id)
                
        except Exception as e:
            log_mcp_error(e, {"context": "response_parsing", "request_id": request_id})
        
        # Log processing time
        print(f"⏱️  Request processed in {processing_time:.3f}s")
        
        return response

def get_custom_entries_for_query(query: str) -> List[Dict[str, Any]]:
    """
    Get custom entries based on the search query.
    
    Args:
        query: The search query
        
    Returns:
        List of custom entries to add
    """
    query_lower = query.lower()
    custom_entries = []
    
    # Check for specific keywords and add relevant custom entries
    for keyword, entries in CUSTOM_ENTRIES.items():
        if keyword in query_lower:
            custom_entries.extend(entries)
    
    # Add a general custom entry if no specific matches
    if not custom_entries:
        custom_entry = {
            "title": "🔧 Enhanced Search Result",
            "link": "https://example.com/enhanced-search",
            "snippet": f"This is an enhanced search result for '{query}'. Custom entries can be configured based on keywords."
        }
        custom_entries.append(custom_entry)
    
    return custom_entries

def enhance_search_results(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Enhance search results with custom entries and modifications.
    
    Args:
        results: Original search results
        query: The search query
        
    Returns:
        Enhanced search results
    """
    # Get custom entries for this query
    custom_entries = get_custom_entries_for_query(query)
    
    # Add custom entries to the beginning
    enhanced_results = custom_entries + results
    
    # Log the enhancement
    print(f"🎯 Enhanced search results for '{query}':")
    print(f"   • Original results: {len(results)}")
    print(f"   • Custom entries added: {len(custom_entries)}")
    print(f"   • Total enhanced results: {len(enhanced_results)}")
    
    return enhanced_results

# --- Define the Web Search Tool with Enhanced Logging ---
def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a web search using the Google Custom Search JSON API.

    Args:
        query (str): The search query string.
        num_results (int): The maximum number of search results to return (default is 5, max is 10).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                               represents a search result with 'title', 'link', and 'snippet'.
                               Returns an empty list if no results or an error occurs.
    """
    # Log the tool call
    tool_args = {"query": query, "num_results": num_results}
    
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        error_msg = "Server configuration error: API keys missing."
        print(f"Error: {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": min(num_results, 10)  # Google Custom Search API max is 10 results per query
    }

    try:
        print(f"🔍 Performing web search for query: '{query}' with {params['num']} results...")
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()

        results = []
        if "items" in search_data:
            for item in search_data["items"]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
            print(f"✅ Found {len(results)} search results.")
        else:
            print("❌ No search results found.")
            if "error" in search_data:
                error_msg = f"Google API Error: {search_data['error'].get('message', 'Unknown error')}"
                print(f"Google API Error: {error_msg}")
                results = [{"error": error_msg}]

        # Log the tool call result
        log_tool_call("search_web", tool_args, results)
        return results

    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error during search: {http_err}"
        print(f"❌ {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result
    except requests.exceptions.ConnectionError as conn_err:
        error_msg = f"Network connection error during search: {conn_err}"
        print(f"❌ {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result
    except requests.exceptions.Timeout as timeout_err:
        error_msg = f"Search request timed out: {timeout_err}"
        print(f"❌ {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Unexpected search request error: {req_err}"
        print(f"❌ {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result
    except json.JSONDecodeError as json_err:
        error_msg = f"Failed to decode API response: {json_err}"
        print(f"❌ {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result
    except Exception as e:
        error_msg = f"An unexpected server error occurred: {e}"
        print(f"❌ {error_msg}")
        result = [{"error": error_msg}]
        log_tool_call("search_web", tool_args, result)
        return result

# Create a FastAPI app
app = FastAPI(title="Enhanced Search Server", description="A web search server with MCP logging and result enhancement")

# Add the MCP logging middleware
app.add_middleware(MCPLoggingMiddleware)

# Manual MCP endpoints
@app.post("/mcp/tools/search_web")
async def mcp_search_web(request: Request):
    """MCP endpoint for search_web tool with result enhancement."""
    try:
        body = await request.json()
        
        # Handle different request formats
        if "params" in body and "arguments" in body["params"]:
            # MCP JSON-RPC format
            args = body["params"]["arguments"]
            query = args.get("query", "")
            num_results = args.get("num_results", 5)
        elif "query" in body:
            # Direct format
            query = body["query"]
            num_results = body.get("num_results", 5)
        else:
            return {"error": "Invalid request format"}
        
        # Call the search function
        results = search_web(query, num_results)
        
        # Hook: Enhance search results with custom entries
        enhanced_results = enhance_search_results(results, query)
        
        # Return in MCP format
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(enhanced_results, indent=2)
                    }
                ]
            }
        }
        
    except Exception as e:
        log_mcp_error(e, {"context": "mcp_search_web"})
        return {
            "jsonrpc": "2.0",
            "id": body.get("id", 1),
            "error": {
                "code": -1,
                "message": str(e)
            }
        }

@app.get("/mcp/tools")
async def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "search_web",
                "description": "Performs a web search using Google Custom Search API with enhanced results",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results (1-10)"}
                    },
                    "required": ["query"]
                }
            }
        ]
    }

@app.get("/custom-entries")
async def get_custom_entries():
    """Get the current custom entries configuration."""
    return {
        "custom_entries": CUSTOM_ENTRIES,
        "description": "Custom entries are automatically added to search results based on keywords"
    }

@app.post("/custom-entries")
async def add_custom_entry(request: Request):
    """Add a new custom entry."""
    try:
        data = await request.json()
        keyword = data.get("keyword")
        entry = data.get("entry")
        
        if not keyword or not entry:
            return {"error": "Missing keyword or entry"}
        
        if keyword not in CUSTOM_ENTRIES:
            CUSTOM_ENTRIES[keyword] = []
        
        CUSTOM_ENTRIES[keyword].append(entry)
        
        return {
            "message": f"Added custom entry for keyword '{keyword}'",
            "custom_entries": CUSTOM_ENTRIES
        }
        
    except Exception as e:
        return {"error": str(e)}

# Add a simple root endpoint for testing
@app.get("/")
def read_root():
    return {
        "message": "Enhanced Search Server with MCP Logging is running", 
        "endpoints": ["/mcp/tools/search_web"],
        "logging": "enabled",
        "enhancement": "enabled"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "logging": "enabled", "enhancement": "enabled"}

@app.get("/logs/stats")
def get_log_stats():
    """Get MCP logging statistics."""
    return mcp_logger.get_statistics()

@app.get("/logs/clear")
def clear_logs():
    """Clear all log files."""
    import shutil
    try:
        shutil.rmtree("mcp_logs")
        os.makedirs("mcp_logs", exist_ok=True)
        return {"message": "Logs cleared successfully"}
    except Exception as e:
        return {"error": f"Failed to clear logs: {str(e)}"}

# --- Main execution block to run the MCP server ---
if __name__ == "__main__":
    print("🚀 Starting Enhanced Search Server with MCP Logging...")
    print("=" * 60)
    print("📊 MCP LOGGING FEATURES:")
    print("   • All requests and responses are logged")
    print("   • Tool calls with arguments and results are captured")
    print("   • Errors are logged with context")
    print("   • Logs are saved to 'mcp_logs/' directory")
    print("   • JSON structured logs for analysis")
    print("   • Real-time console output")
    print()
    print("🎯 RESULT ENHANCEMENT FEATURES:")
    print("   • Custom entries added based on keywords")
    print("   • Configurable custom entries")
    print("   • Dynamic result enhancement")
    print("   • Keyword-based matching")
    print()
    print("📁 LOG FILES:")
    print("   • mcp_requests.jsonl - All incoming requests")
    print("   • mcp_responses.jsonl - All outgoing responses")
    print("   • mcp_tool_calls.jsonl - Tool calls with results")
    print("   • mcp_errors.jsonl - Error logs")
    print("   • mcp_traffic_*.log - Detailed traffic logs")
    print()
    print("🔗 ENDPOINTS:")
    print("   • GET / - Server info")
    print("   • GET /health - Health check")
    print("   • GET /logs/stats - Logging statistics")
    print("   • GET /logs/clear - Clear all logs")
    print("   • POST /mcp/tools/search_web - Web search tool")
    print("   • GET /mcp/tools - List available tools")
    print("   • GET /custom-entries - View custom entries")
    print("   • POST /custom-entries - Add custom entry")
    print()
    print("To run this server, use:")
    print("uvicorn enhanced_search_server:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("The server will be accessible at http://localhost:8000")
    print("Ensure your .env file with GOOGLE_API_KEY and GOOGLE_CSE_ID is in the same directory.")
    print("=" * 60) 