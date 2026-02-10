# eBay MCP Server

A Model Context Protocol (MCP) server for interacting with eBay's APIs. Enables AI assistants to search eBay listings, track prices, and find deals on homelab equipment and other items.

## Features

### ✅ Implemented (8 tools)
- 🔍 **Search eBay listings** - Basic and advanced search with all filters
- 💰 **Price tracking** - SQLite database tracks prices over time
- 📊 **Deal detection** - Analyzes market data to find bargains (15%+ below average)
- 📦 **Item details** - Comprehensive info including seller reputation
- 📈 **Price history** - View trends with statistics (min/max/avg/median)
- 📋 **Watchlist** - Track multiple items with custom alerts

### 🚧 Planned (12 tools)
- 🏷️ **Category browsing** - Navigate eBay's category hierarchy
- 🆕 **New listings** - Fresh deals (last 6-24 hours)
- ⏰ **Ending soon** - Auction sniper helper
- 📊 **Market value** - Price research tool

## Status

🟢 **MVP Complete** - 8 core tools implemented and ready for testing!

See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for detailed progress.

## Planned Tools

- `search_ebay` - Search listings with filters (keywords, price, condition, category)
- `get_item_details` - Get detailed information about a specific listing
- `track_price` - Add an item to price tracking
- `get_price_history` - View historical price data for tracked items
- `find_deals` - Search for items below market value based on historical data

## Requirements

- Python 3.10+
- eBay Developer Account (for API credentials)
- MCP-compatible client (Claude Desktop, Cline, etc.)

## Quick Start

1. **Get eBay API Credentials**
   - Sign up at https://developer.ebay.com/
   - Create an application
   - Copy your App ID

2. **Install**
   ```bash
   git clone https://github.com/hanku4u/ebay-mcp-server.git
   cd ebay-mcp-server
   pip install -e .
   ```

3. **Configure**
   ```bash
   cp .env.example .env
   # Edit .env and add your EBAY_APP_ID
   ```

4. **Test**
   ```bash
   python -m ebay_mcp
   # Server will start in stdio mode (MCP standard)
   ```

## Configuration

Set your eBay API credentials as environment variables:

```bash
export EBAY_APP_ID="your-app-id"
export EBAY_CERT_ID="your-cert-id"
export EBAY_DEV_ID="your-dev-id"
```

Or create a `.env` file:

```
EBAY_APP_ID=your-app-id
EBAY_CERT_ID=your-cert-id
EBAY_DEV_ID=your-dev-id
```

## Usage

### With Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ebay": {
      "command": "python",
      "args": ["-m", "ebay_mcp"],
      "env": {
        "EBAY_APP_ID": "your-app-id",
        "EBAY_CERT_ID": "your-cert-id",
        "EBAY_DEV_ID": "your-dev-id"
      }
    }
  }
}

Alternatively, use the FastMCP CLI:

```json
{
  "mcpServers": {
    "ebay": {
      "command": "fastmcp",
      "args": ["run", "path/to/ebay_mcp/server.py:mcp"],
      "env": {
        "EBAY_APP_ID": "your-app-id",
        "EBAY_CERT_ID": "your-cert-id",
        "EBAY_DEV_ID": "your-dev-id"
      }
    }
  }
}
```

### With OpenClaw

Coming soon - will integrate with OpenClaw's MCP client capabilities.

### HTTP Server (Remote Access)

Run as an HTTP server for remote access:

```bash
python -m ebay_mcp
# Or with FastMCP CLI:
fastmcp run src/ebay_mcp/server.py:mcp --transport http --port 8000
```

Then connect from any MCP client:

```python
from fastmcp import Client

async with Client("http://localhost:8000/mcp") as client:
    result = await client.call_tool("search_ebay", {
        "keywords": "Dell PowerEdge R720",
        "max_price": 500
    })
    print(result)
```

## eBay API Access

To use this server, you'll need eBay API credentials:

1. Sign up for the [eBay Developers Program](https://developer.ebay.com/)
2. Create a new application
3. Generate your App ID, Cert ID, and Dev ID
4. Choose the appropriate API: Finding API (for search) or Trading API (for account management)

## Recurring Searches with OpenClaw

Example cron job for daily homelab equipment searches:

```json
{
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "America/Chicago" },
  "payload": {
    "kind": "agentTurn",
    "message": "Search eBay for homelab servers under $500 and summarize the best deals"
  },
  "sessionTarget": "isolated"
}
```

## Architecture

Built using [FastMCP](https://gofastmcp.com) - the fast, Pythonic way to build MCP servers. FastMCP powers 70% of MCP servers and makes it easy to create production-ready integrations with minimal boilerplate.

### Example: Adding a Tool

Adding new tools is as simple as decorating a function:

```python
from fastmcp import FastMCP

mcp = FastMCP("eBay MCP Server")

@mcp.tool
def search_ebay(
    keywords: str,
    max_price: float = None,
    condition: str = "New"
) -> dict:
    """Search eBay listings with filters"""
    # Implementation here
    return {...}

if __name__ == "__main__":
    mcp.run()  # Supports stdio and HTTP transports
```

FastMCP automatically:
- Generates JSON schemas from type hints
- Validates inputs with Pydantic
- Handles MCP protocol serialization
- Provides both stdio and HTTP transports

## License

MIT

## Contributing

Contributions welcome! This is an early-stage project focused on homelab deal hunting.

## Author

Created by [@hanku4u](https://github.com/hanku4u) with AI assistance from RockLobster 🦞
