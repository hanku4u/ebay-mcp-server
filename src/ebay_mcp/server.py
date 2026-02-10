"""eBay MCP Server implementation using FastMCP."""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from fastmcp import FastMCP

from .ebay_client import EbayAPIClient
from .database import PriceTrackingDB

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("eBay MCP Server")

# Initialize eBay API client (will use environment variables)
try:
    ebay_client = EbayAPIClient()
    print("✅ eBay API client initialized")
except ValueError as e:
    ebay_client = None
    print(f"⚠️  {e}")
    print("   Set EBAY_APP_ID in .env file or environment variables")

# Initialize price tracking database
db = PriceTrackingDB()
print("✅ Price tracking database initialized")


@mcp.tool
def search_ebay(
    keywords: str,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    condition: Optional[str] = None,
    category_id: Optional[str] = None,
    sort_by: str = "BestMatch",
    limit: int = 20
) -> dict:
    """
    Search eBay listings with basic filters.
    
    Args:
        keywords: Search keywords (e.g., 'Dell PowerEdge R720')
        max_price: Maximum price in USD
        min_price: Minimum price in USD
        condition: Item condition ('New', 'Used', 'Refurbished', 'For parts or not working')
        category_id: eBay category ID (e.g., '175673' for Computer Servers)
        sort_by: Sort order ('BestMatch', 'PricePlusShippingLowest', 'PricePlusShippingHighest', 'EndTimeSoonest')
        limit: Maximum number of results (1-100)
    
    Returns:
        Search results with item listings
    """
    if not ebay_client:
        return {
            "status": "error",
            "message": "eBay API not configured. Set EBAY_APP_ID environment variable."
        }
    
    return ebay_client.search(
        keywords=keywords,
        max_price=max_price,
        min_price=min_price,
        condition=condition,
        category_id=category_id,
        sort_by=sort_by,
        limit=limit
    )


@mcp.tool
def search_ebay_advanced(
    keywords: str,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    condition: Optional[str] = None,
    category_id: Optional[str] = None,
    sort_by: str = "BestMatch",
    limit: int = 20,
    free_shipping_only: bool = False,
    local_pickup_only: bool = False,
    sold_items_only: bool = False,
    exclude_keywords: Optional[str] = None,
    seller_type: Optional[str] = None
) -> dict:
    """
    Advanced eBay search with granular filtering.
    
    Args:
        keywords: Search keywords
        max_price: Maximum price in USD
        min_price: Minimum price in USD
        condition: Item condition
        category_id: eBay category ID
        sort_by: Sort order
        limit: Maximum number of results (1-100)
        free_shipping_only: Only items with free shipping
        local_pickup_only: Only items with local pickup
        sold_items_only: Show completed/sold listings (market research)
        exclude_keywords: Keywords to exclude from results
        seller_type: 'Business' or 'Individual'
    
    Returns:
        Filtered search results
    """
    if not ebay_client:
        return {
            "status": "error",
            "message": "eBay API not configured. Set EBAY_APP_ID environment variable."
        }
    
    # Build advanced filters
    item_filter = {}
    
    if free_shipping_only:
        item_filter['FreeShippingOnly'] = 'true'
    
    if local_pickup_only:
        item_filter['LocalPickupOnly'] = 'true'
    
    if sold_items_only:
        item_filter['SoldItemsOnly'] = 'true'
    
    if seller_type:
        item_filter['SellerBusinessType'] = seller_type
    
    # Modify keywords to exclude terms
    final_keywords = keywords
    if exclude_keywords:
        exclude_terms = exclude_keywords.split(',')
        for term in exclude_terms:
            final_keywords += f" -{term.strip()}"
    
    return ebay_client.search(
        keywords=final_keywords,
        max_price=max_price,
        min_price=min_price,
        condition=condition,
        category_id=category_id,
        sort_by=sort_by,
        limit=limit,
        item_filter=item_filter
    )


@mcp.tool
def get_item_details(item_id: str) -> dict:
    """
    Get detailed information about a specific eBay listing.
    
    Args:
        item_id: eBay item ID
    
    Returns:
        Comprehensive item details including price, condition, shipping, seller info, photos
    """
    if not ebay_client:
        return {
            "status": "error",
            "message": "eBay API not configured. Set EBAY_APP_ID environment variable."
        }
    
    return ebay_client.get_item_details(item_id)


@mcp.tool
def track_price(
    item_id: str,
    title: str = "",
    current_price: float = 0.0,
    alert_threshold: Optional[float] = None,
    alert_percentage: Optional[float] = None,
    notes: str = ""
) -> dict:
    """
    Add an item to the price tracking watchlist.
    
    Args:
        item_id: eBay item ID to track
        title: Item title (will be fetched if not provided)
        current_price: Current item price (will be fetched if not provided)
        alert_threshold: Alert when price drops below this amount (USD)
        alert_percentage: Alert on X% price drop (e.g., 15 for 15%)
        notes: Personal notes about why tracking this item
    
    Returns:
        Confirmation of tracking setup with initial price
    """
    # Fetch item details if not provided
    if not title or current_price == 0.0:
        if ebay_client:
            details = ebay_client.get_item_details(item_id)
            if details.get('status') == 'success':
                title = title or details.get('title', '')
                current_price = current_price or details.get('price', {}).get('current', 0.0)
                url = details.get('urls', {}).get('view_item', '')
                category = details.get('listing_info', {}).get('listing_type', '')
            else:
                return details  # Return error from API
        else:
            return {
                "status": "error",
                "message": "eBay API not configured and item details not provided"
            }
    else:
        url = f"https://www.ebay.com/itm/{item_id}"
        category = ""
    
    return db.track_item(
        item_id=item_id,
        title=title,
        current_price=current_price,
        url=url,
        category=category,
        alert_threshold=alert_threshold,
        alert_percentage=alert_percentage,
        notes=notes
    )


@mcp.tool
def untrack_price(item_id: str, delete_history: bool = False) -> dict:
    """
    Remove an item from price tracking.
    
    Args:
        item_id: eBay item ID to stop tracking
        delete_history: If true, permanently delete all price history (default: false, keeps history)
    
    Returns:
        Confirmation message
    """
    return db.untrack_item(item_id, delete_history)


@mcp.tool
def get_price_history(item_id: str, days: int = 30) -> dict:
    """
    View historical price data for a tracked item.
    
    Args:
        item_id: eBay item ID
        days: Number of days of history to retrieve (default: 30)
    
    Returns:
        Price history with trend analysis (min, max, average, median, trend direction)
    """
    return db.get_price_history(item_id, days)


@mcp.tool
def list_tracked_items(active_only: bool = True, sort_by: str = "date_added") -> dict:
    """
    View all items in your price tracking watchlist.
    
    Args:
        active_only: Only show items currently being tracked (default: true)
        sort_by: Sort order ('date_added', 'current_price')
    
    Returns:
        List of tracked items with current prices and alert settings
    """
    items = db.list_tracked_items(active_only, sort_by)
    return {
        "status": "success",
        "tracked_count": len(items),
        "items": items
    }


@mcp.tool
def find_deals(
    keywords: str,
    discount_threshold: float = 15.0,
    limit: int = 10,
    condition: Optional[str] = None
) -> dict:
    """
    Find items priced below market value based on sold listings analysis.
    
    Args:
        keywords: Search keywords (e.g., 'Dell R720')
        discount_threshold: Minimum discount percentage from average price (default: 15%)
        limit: Maximum number of deals to return (default: 10)
        condition: Filter by condition (optional)
    
    Returns:
        List of deals ranked by discount percentage and deal quality score
    """
    if not ebay_client:
        return {
            "status": "error",
            "message": "eBay API not configured. Set EBAY_APP_ID environment variable."
        }
    
    # Get completed/sold listings for market analysis
    sold_items = ebay_client.get_completed_listings(keywords, days=90, limit=100)
    
    if not sold_items:
        return {
            "status": "error",
            "message": "Not enough market data to analyze deals. Try different keywords."
        }
    
    # Calculate market statistics
    prices = [item['price'] for item in sold_items if item['price'] > 0]
    if not prices:
        return {
            "status": "error",
            "message": "No valid price data found in sold listings"
        }
    
    average_price = sum(prices) / len(prices)
    median_price = sorted(prices)[len(prices) // 2]
    min_price = min(prices)
    max_price = max(prices)
    
    # Search for active listings
    active_listings = ebay_client.search(
        keywords=keywords,
        condition=condition,
        limit=50
    )
    
    if active_listings.get('status') != 'success' or not active_listings.get('items'):
        return {
            "status": "error",
            "message": "No active listings found matching criteria"
        }
    
    # Find deals below market value
    deals = []
    threshold_price = average_price * (1 - discount_threshold / 100)
    
    for item in active_listings['items']:
        item_price = item['price']
        
        if item_price <= threshold_price and item_price > 0:
            discount_amount = average_price - item_price
            discount_percent = (discount_amount / average_price) * 100
            
            # Calculate deal score (0-10)
            # Factors: discount %, price stability, condition
            price_score = min(discount_percent / 10, 5)  # Max 5 points for discount
            condition_score = {'New': 3, 'Refurbished': 2, 'Used': 1}.get(
                item.get('condition', 'Used').split(' - ')[0], 0
            )
            shipping_score = 2 if item.get('shipping_cost', 0) == 0 else 0
            
            deal_score = price_score + condition_score + shipping_score
            
            deals.append({
                'item_id': item['item_id'],
                'title': item['title'],
                'url': item['url'],
                'current_price': round(item_price, 2),
                'market_price': round(average_price, 2),
                'discount_amount': round(discount_amount, 2),
                'discount_percent': round(discount_percent, 1),
                'deal_score': round(deal_score, 1),
                'condition': item.get('condition', 'Unknown'),
                'shipping_cost': item.get('shipping_cost', 0),
                'location': item.get('location', ''),
                'time_left': item.get('time_left', ''),
                'image_url': item.get('image_url', '')
            })
    
    # Sort by deal score (descending)
    deals.sort(key=lambda x: x['deal_score'], reverse=True)
    
    return {
        "status": "success",
        "keyword": keywords,
        "market_analysis": {
            "sample_size": len(sold_items),
            "average_price": round(average_price, 2),
            "median_price": round(median_price, 2),
            "price_range": [round(min_price, 2), round(max_price, 2)]
        },
        "discount_threshold": discount_threshold,
        "deals_found": len(deals),
        "deals": deals[:limit]
    }


if __name__ == "__main__":
    # Run with stdio (default for MCP clients like Claude Desktop)
    mcp.run()
    
    # Alternative: Run with HTTP for remote access
    # mcp.run(transport="http", port=8000)
