# eBay MCP Server

A Model Context Protocol (MCP) server for interacting with eBay's APIs. Enables AI assistants to search eBay listings, track prices, and find deals on homelab equipment and other items.

## Features

- 🔍 **Search eBay listings** - Search by keywords, category, price range, condition
- 💰 **Price tracking** - Monitor item prices over time
- 📊 **Deal detection** - Find items below typical market price
- 🏷️ **Category browsing** - Navigate eBay's category hierarchy
- 📦 **Item details** - Get comprehensive item information

## Status

🚧 **Work in Progress** - Initial development phase

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

## Installation

```bash
# Clone the repository
git clone https://github.com/hanku4u/ebay-mcp-server.git
cd ebay-mcp-server

# Install dependencies
pip install -e .
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
```

### With OpenClaw

Coming soon - will integrate with OpenClaw's MCP client capabilities.

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

Built using the [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk) for seamless integration with MCP-compatible AI assistants.

## License

MIT

## Contributing

Contributions welcome! This is an early-stage project focused on homelab deal hunting.

## Author

Created by [@hanku4u](https://github.com/hanku4u) with AI assistance from RockLobster 🦞
