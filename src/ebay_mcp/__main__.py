"""Entry point for running the eBay MCP server as a module."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
