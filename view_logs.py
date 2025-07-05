#!/usr/bin/env python3
"""
MCP Log Viewer - View and analyze MCP logs in real-time

This script provides tools to view and analyze the MCP traffic logs
captured by the search server.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import argparse


class MCPLogViewer:
    """Viewer for MCP logs."""
    
    def __init__(self, log_dir: str = "mcp_logs"):
        self.log_dir = Path(log_dir)
        self.log_files = {
            "requests": self.log_dir / "mcp_requests.jsonl",
            "responses": self.log_dir / "mcp_responses.jsonl",
            "tool_calls": self.log_dir / "mcp_tool_calls.jsonl",
            "errors": self.log_dir / "mcp_errors.jsonl"
        }
    
    def check_logs_exist(self) -> bool:
        """Check if any log files exist."""
        return any(f.exists() for f in self.log_files.values())
    
    def read_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read a JSONL file and return list of JSON objects."""
        if not file_path.exists():
            return []
        
        entries = []
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        return entries
    
    def view_recent_requests(self, limit: int = 10):
        """View recent MCP requests."""
        requests = self.read_jsonl_file(self.log_files["requests"])
        print(f"\n📥 RECENT MCP REQUESTS (last {min(limit, len(requests))}):")
        print("=" * 60)
        
        for entry in requests[-limit:]:
            timestamp = entry.get("timestamp", "unknown")
            request_id = entry.get("request_id", "unknown")
            method = entry.get("data", {}).get("method", "unknown")
            
            print(f"🕒 {timestamp}")
            print(f"🆔 {request_id}")
            print(f"📋 Method: {method}")
            
            # Show request details
            data = entry.get("data", {})
            if "params" in data:
                params = data["params"]
                if "name" in params:
                    print(f"🔧 Tool: {params['name']}")
                if "arguments" in params:
                    args = params["arguments"]
                    print(f"📝 Arguments: {json.dumps(args, indent=2)}")
            
            print("-" * 40)
    
    def view_recent_responses(self, limit: int = 10):
        """View recent MCP responses."""
        responses = self.read_jsonl_file(self.log_files["responses"])
        print(f"\n📤 RECENT MCP RESPONSES (last {min(limit, len(responses))}):")
        print("=" * 60)
        
        for entry in responses[-limit:]:
            timestamp = entry.get("timestamp", "unknown")
            request_id = entry.get("request_id", "unknown")
            
            print(f"🕒 {timestamp}")
            print(f"🆔 {request_id}")
            
            # Show response details
            data = entry.get("data", {})
            if "result" in data:
                result = data["result"]
                if "content" in result:
                    content = result["content"]
                    print(f"📄 Content: {json.dumps(content, indent=2)}")
            
            print("-" * 40)
    
    def view_tool_calls(self, limit: int = 10):
        """View recent tool calls."""
        tool_calls = self.read_jsonl_file(self.log_files["tool_calls"])
        print(f"\n🔧 RECENT TOOL CALLS (last {min(limit, len(tool_calls))}):")
        print("=" * 60)
        
        for entry in tool_calls[-limit:]:
            timestamp = entry.get("timestamp", "unknown")
            tool_name = entry.get("tool_name", "unknown")
            arguments = entry.get("arguments", {})
            result = entry.get("result", {})
            
            print(f"🕒 {timestamp}")
            print(f"🔧 Tool: {tool_name}")
            print(f"📝 Arguments: {json.dumps(arguments, indent=2)}")
            print(f"📊 Result: {json.dumps(result, indent=2)}")
            print("-" * 40)
    
    def view_errors(self, limit: int = 10):
        """View recent errors."""
        errors = self.read_jsonl_file(self.log_files["errors"])
        print(f"\n❌ RECENT ERRORS (last {min(limit, len(errors))}):")
        print("=" * 60)
        
        for entry in errors[-limit:]:
            timestamp = entry.get("timestamp", "unknown")
            error_type = entry.get("error_type", "unknown")
            error_message = entry.get("error_message", "unknown")
            context = entry.get("context", {})
            
            print(f"🕒 {timestamp}")
            print(f"🚨 Type: {error_type}")
            print(f"💬 Message: {error_message}")
            if context:
                print(f"🔍 Context: {json.dumps(context, indent=2)}")
            print("-" * 40)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get log statistics."""
        stats = {}
        for name, file_path in self.log_files.items():
            entries = self.read_jsonl_file(file_path)
            stats[name] = len(entries)
        
        return stats
    
    def print_statistics(self):
        """Print log statistics."""
        stats = self.get_statistics()
        print("\n📊 MCP LOG STATISTICS:")
        print("=" * 30)
        for name, count in stats.items():
            print(f"   {name}: {count} entries")
        
        total = sum(stats.values())
        print(f"   Total: {total} entries")
    
    def tail_logs(self, file_type: str = "all", follow: bool = True):
        """Tail logs in real-time."""
        if file_type not in self.log_files and file_type != "all":
            print(f"❌ Unknown log type: {file_type}")
            return
        
        print(f"👀 Tailing {file_type} logs... (Press Ctrl+C to stop)")
        print("=" * 50)
        
        try:
            while True:
                if file_type == "all":
                    for name, file_path in self.log_files.items():
                        if file_path.exists():
                            self._tail_file(file_path, name)
                else:
                    file_path = self.log_files[file_type]
                    if file_path.exists():
                        self._tail_file(file_path, file_type)
                
                if not follow:
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Stopped tailing logs.")
    
    def _tail_file(self, file_path: Path, file_type: str):
        """Tail a specific log file."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    try:
                        entry = json.loads(last_line)
                        timestamp = entry.get("timestamp", "unknown")
                        print(f"[{timestamp}] {file_type.upper()}: {json.dumps(entry, indent=2)}")
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"Error reading {file_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="MCP Log Viewer")
    parser.add_argument("--log-dir", default="mcp_logs", help="Log directory")
    parser.add_argument("--limit", type=int, default=10, help="Number of entries to show")
    parser.add_argument("--type", choices=["requests", "responses", "tool_calls", "errors", "all"], 
                       default="all", help="Type of logs to view")
    parser.add_argument("--tail", action="store_true", help="Tail logs in real-time")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    
    args = parser.parse_args()
    
    viewer = MCPLogViewer(args.log_dir)
    
    if not viewer.check_logs_exist():
        print("❌ No log files found. Make sure the server is running and generating logs.")
        return
    
    if args.stats:
        viewer.print_statistics()
        return
    
    if args.tail:
        viewer.tail_logs(args.type, follow=True)
        return
    
    # Show all log types
    if args.type == "all":
        viewer.print_statistics()
        viewer.view_recent_requests(args.limit)
        viewer.view_recent_responses(args.limit)
        viewer.view_tool_calls(args.limit)
        viewer.view_errors(args.limit)
    elif args.type == "requests":
        viewer.view_recent_requests(args.limit)
    elif args.type == "responses":
        viewer.view_recent_responses(args.limit)
    elif args.type == "tool_calls":
        viewer.view_tool_calls(args.limit)
    elif args.type == "errors":
        viewer.view_errors(args.limit)


if __name__ == "__main__":
    main() 