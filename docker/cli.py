"""CLI entry point for WebCat MCP server with demo UI support."""

import argparse
import os
import sys

def main():
    """Main CLI entry point for WebCat server."""
    parser = argparse.ArgumentParser(
        description="WebCat MCP Server - Web search and content extraction with MCP protocol support"
    )
    
    parser.add_argument(
        "--mode",
        choices=["mcp", "demo"],
        default="mcp",
        help="Server mode: 'mcp' for standard MCP server, 'demo' for demo server with UI"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8000)),
        help="Port to listen on (default: 8000, or PORT env var)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set environment variables from arguments
    os.environ["LOG_LEVEL"] = args.log_level
    
    if args.mode == "demo":
        print("🐱 Starting WebCat in DEMO mode with UI...")
        print(f"   Host: {args.host}")
        print(f"   Port: {args.port} (unified server - all endpoints)")
        print(f"   Log Level: {args.log_level}")
        print()
        
        try:
            from simple_demo import run_simple_demo
            run_simple_demo(host=args.host, port=args.port)
        except ImportError as e:
            print(f"❌ Error importing demo server: {e}")
            print("Make sure all dependencies are installed.")
            sys.exit(1)
    
    else:
        print("🐱 Starting WebCat in MCP mode...")
        print(f"   Host: {args.host}")
        print(f"   Port: {args.port}")
        print(f"   Log Level: {args.log_level}")
        print()
        
        try:
            # Import and run the original MCP server
            from mcp_server import mcp_server
            import uvicorn
            
            print(f"📡 WebCat MCP Server: http://{args.host}:{args.port}/mcp")
            print("✨ Ready for MCP connections!")
            
            # Run the FastMCP server
            mcp_server.run(
                transport="sse",
                host=args.host,
                port=args.port,
                path="/mcp"
            )
        except ImportError as e:
            print(f"❌ Error importing MCP server: {e}")
            print("Make sure all dependencies are installed.")
            sys.exit(1)

if __name__ == "__main__":
    main()
