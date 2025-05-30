"""Entry point for the MCP server."""

import os
import uvicorn
from mcp import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("mcp:app", host="0.0.0.0", port=port, reload=False) 