import os
import json
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
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

# Initialize FastMCP server
mcp = FastMCP("OnlineSearch")

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

# --- Define the Web Search Tool with Enhanced Logging ---
@mcp.tool()
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

# Create a FastAPI app and add the MCP routes
app = FastAPI(title="Search Server with MCP Logging", description="A web search server using FastMCP with comprehensive logging")

# Add the MCP logging middleware
app.add_middleware(MCPLoggingMiddleware)

# Add the MCP routes to the FastAPI app
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)

# Add a simple root endpoint for testing
@app.get("/")
def read_root():
    return {
        "message": "Search Server with MCP Logging is running", 
        "endpoints": ["/mcp/tools/search_web"],
        "logging": "enabled"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "logging": "enabled"}

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
    print("🚀 Starting FastMCP server with comprehensive logging...")
    print("=" * 60)
    print("📊 MCP LOGGING FEATURES:")
    print("   • All requests and responses are logged")
    print("   • Tool calls with arguments and results are captured")
    print("   • Errors are logged with context")
    print("   • Logs are saved to 'mcp_logs/' directory")
    print("   • JSON structured logs for analysis")
    print("   • Real-time console output")
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
    print()
    print("To run this server, use:")
    print("uvicorn search_server_with_logging:app --host 0.0.0.0 --port 8000 --reload")
    print()
    print("The server will be accessible at http://localhost:8000")
    print("Ensure your .env file with GOOGLE_API_KEY and GOOGLE_CSE_ID is in the same directory.")
    print("=" * 60) 