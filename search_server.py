import os
import json
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import List, Dict, Any
from fastapi import FastAPI

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and CSE ID from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize FastMCP server
# The name "OnlineSearch" will be used by the MCP client to identify this server
mcp = FastMCP("OnlineSearch")

# --- Define the Web Search Tool ---
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
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("Error: Google API Key or Custom Search Engine ID not set in environment variables.")
        return [{"error": "Server configuration error: API keys missing."}]

    search_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": min(num_results, 10)  # Google Custom Search API max is 10 results per query
    }

    try:
        print(f"Performing web search for query: '{query}' with {params['num']} results...")
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        search_data = response.json()

        results = []
        if "items" in search_data:
            for item in search_data["items"]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                })
            print(f"Found {len(results)} search results.")
        else:
            print("No search results found.")
            if "error" in search_data:
                print(f"Google API Error: {search_data['error'].get('message', 'Unknown error')}")
                return [{"error": f"Google API Error: {search_data['error'].get('message', 'Unknown error')}"}]

        return results

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return [{"error": f"HTTP error during search: {http_err}"}]
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return [{"error": f"Network connection error during search: {conn_err}"}]
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        return [{"error": f"Search request timed out: {timeout_err}"}]
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return [{"error": f"Unexpected search request error: {req_err}"}]
    except json.JSONDecodeError as json_err:
        print(f"JSON decode error: {json_err}")
        return [{"error": f"Failed to decode API response: {json_err}"}]
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return [{"error": f"An unexpected server error occurred: {e}"}]

# Create a FastAPI app and add the MCP routes
app = FastAPI(title="Search Server", description="A web search server using FastMCP")

# Add the MCP routes to the FastAPI app
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)

# Add a simple root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Search Server is running", "endpoints": ["/mcp/tools/search_web"]}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- Main execution block to run the MCP server ---
if __name__ == "__main__":
    # To run this as an HTTP server (recommended for "online" access),
    # you'll use uvicorn.
    # The FastMCP app is automatically created and accessible via `mcp.app`.
    print("Starting FastMCP server...")
    print("To run this server, use the following command in your terminal:")
    print("uvicorn search_server:app --host 0.0.0.0 --port 8000 --reload")
    print("\nThe server will be accessible at http://localhost:8000")
    print("Available endpoints:")
    print("- GET / - Server info")
    print("- GET /health - Health check")
    print("- POST /mcp/tools/search_web - Web search tool")
    print("Ensure your .env file with GOOGLE_API_KEY and GOOGLE_CSE_ID is in the same directory.")

    # Note: The `mcp.run_stdio()` method is for local testing via standard I/O,
    # which is not suitable for an "online" server accessible via HTTP.
    # The uvicorn command above is the correct way to run it as an HTTP server.