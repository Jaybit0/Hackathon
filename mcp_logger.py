#!/usr/bin/env python3
"""
MCP Logger - Captures and logs raw MCP input/output traffic

This module provides logging capabilities for Model Context Protocol (MCP) traffic,
allowing you to see the raw requests and responses being exchanged.
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os


class MCPLogger:
    """Logger for capturing MCP traffic."""
    
    def __init__(self, log_dir: str = "mcp_logs", log_level: str = "INFO"):
        """
        Initialize the MCP logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("mcp_traffic")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create handlers
        self._setup_handlers()
        
        # Statistics
        self.request_count = 0
        self.response_count = 0
        self.error_count = 0
    
    def _setup_handlers(self):
        """Set up logging handlers."""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for detailed logs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(
            self.log_dir / f"mcp_traffic_{timestamp}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # JSON handler for structured logging
        json_handler = logging.FileHandler(
            self.log_dir / f"mcp_structured_{timestamp}.jsonl"
        )
        json_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(json_handler)
    
    def log_request(self, request_data: Dict[str, Any], request_id: Optional[str] = None):
        """
        Log an incoming MCP request.
        
        Args:
            request_data: The request data dictionary
            request_id: Optional request ID for tracking
        """
        self.request_count += 1
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "type": "request",
            "request_id": request_id or f"req_{self.request_count}",
            "data": request_data
        }
        
        # Log to console
        self.logger.info(f"📥 MCP REQUEST #{self.request_count}: {request_data.get('method', 'unknown')}")
        
        # Log detailed data to file
        self.logger.debug(f"REQUEST DETAILS: {json.dumps(log_entry, indent=2)}")
        
        # Save to JSON file
        with open(self.log_dir / "mcp_requests.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_response(self, response_data: Dict[str, Any], request_id: Optional[str] = None):
        """
        Log an outgoing MCP response.
        
        Args:
            response_data: The response data dictionary
            request_id: Optional request ID for tracking
        """
        self.response_count += 1
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "type": "response",
            "request_id": request_id or f"req_{self.response_count}",
            "data": response_data
        }
        
        # Log to console
        self.logger.info(f"📤 MCP RESPONSE #{self.response_count}")
        
        # Log detailed data to file
        self.logger.debug(f"RESPONSE DETAILS: {json.dumps(log_entry, indent=2)}")
        
        # Save to JSON file
        with open(self.log_dir / "mcp_responses.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log an MCP error.
        
        Args:
            error: The exception that occurred
            context: Optional context information
        """
        self.error_count += 1
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "type": "error",
            "error_count": self.error_count,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        # Log to console
        self.logger.error(f"❌ MCP ERROR #{self.error_count}: {error}")
        
        # Log detailed data to file
        self.logger.debug(f"ERROR DETAILS: {json.dumps(log_entry, indent=2)}")
        
        # Save to JSON file
        with open(self.log_dir / "mcp_errors.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_tool_call(self, tool_name: str, tool_args: Dict[str, Any], result: Any):
        """
        Log a tool call with its arguments and result.
        
        Args:
            tool_name: Name of the tool being called
            tool_args: Arguments passed to the tool
            result: Result returned by the tool
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "type": "tool_call",
            "tool_name": tool_name,
            "arguments": tool_args,
            "result": result
        }
        
        # Log to console
        self.logger.info(f"🔧 TOOL CALL: {tool_name}")
        
        # Log detailed data to file
        self.logger.debug(f"TOOL CALL DETAILS: {json.dumps(log_entry, indent=2)}")
        
        # Save to JSON file
        with open(self.log_dir / "mcp_tool_calls.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "requests_logged": self.request_count,
            "responses_logged": self.response_count,
            "errors_logged": self.error_count,
            "log_directory": str(self.log_dir),
            "timestamp": datetime.now().isoformat()
        }
    
    def print_statistics(self):
        """Print current logging statistics."""
        stats = self.get_statistics()
        print("\n📊 MCP LOGGING STATISTICS:")
        print(f"   Requests logged: {stats['requests_logged']}")
        print(f"   Responses logged: {stats['responses_logged']}")
        print(f"   Errors logged: {stats['errors_logged']}")
        print(f"   Log directory: {stats['log_directory']}")


# Global logger instance
mcp_logger = MCPLogger()


def log_mcp_request(request_data: Dict[str, Any], request_id: Optional[str] = None):
    """Convenience function to log MCP requests."""
    mcp_logger.log_request(request_data, request_id)


def log_mcp_response(response_data: Dict[str, Any], request_id: Optional[str] = None):
    """Convenience function to log MCP responses."""
    mcp_logger.log_response(response_data, request_id)


def log_mcp_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """Convenience function to log MCP errors."""
    mcp_logger.log_error(error, context)


def log_tool_call(tool_name: str, tool_args: Dict[str, Any], result: Any):
    """Convenience function to log tool calls."""
    mcp_logger.log_tool_call(tool_name, tool_args, result)


if __name__ == "__main__":
    # Test the logger
    print("Testing MCP Logger...")
    
    # Test request logging
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "search_web",
            "arguments": {"query": "test query", "num_results": 3}
        }
    }
    
    log_mcp_request(test_request, "test_req_1")
    
    # Test response logging
    test_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [
                {"type": "text", "text": "Search results..."}
            ]
        }
    }
    
    log_mcp_response(test_response, "test_req_1")
    
    # Test tool call logging
    log_tool_call("search_web", {"query": "test"}, [{"title": "Test Result"}])
    
    # Print statistics
    mcp_logger.print_statistics()
    
    print("✅ MCP Logger test completed!") 