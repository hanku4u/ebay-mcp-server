# eBay MCP Server - Feature Planning

## Phase 1: Core Search & Discovery (MVP)

### 🔍 Search Tools

#### 1. `search_ebay` - General Search
**What it does:** Basic keyword search with essential filters
**Parameters:**
- `keywords` (required) - Search terms
- `limit` - Results to return (default: 20, max: 100)
- `sort_by` - BestMatch, PricePlusShippingLowest, EndTimeSoonest, etc.

**Use case:** "Search eBay for Dell PowerEdge servers"

#### 2. `search_ebay_advanced` - Refined Search
**What it does:** Granular filtering for power users
**Parameters:**
- `keywords` (required)
- `price_min` / `price_max` - Price range
- `condition` - New, Used, Refurbished, For parts
- `item_location` - Country/region filter
- `shipping_options` - FreeShippingOnly, LocalPickupOnly, etc.
- `seller_type` - Business, Individual
- `listing_type` - Auction, FixedPrice, BestOffer
- `item_description` - Search in descriptions too (slower but thorough)
- `exclude_keywords` - Filter out unwanted results
- `category_id` - Narrow to specific category
- `sold_items` - Show completed/sold listings for market research

**Use case:** "Search for used Dell R720 servers under $400, refurbished condition, free shipping, with 'rails' in description, exclude 'broken' and 'parts'"

#### 3. `search_by_category` - Category Browser
**What it does:** Browse eBay's category hierarchy
**Parameters:**
- `category_id` - Starting category
- `depth` - How many levels deep to show
- `include_counts` - Show item counts per category

**Common homelab categories:**
- 175673 - Computer Servers
- 175698 - Enterprise Networking & Servers > Networking
- 182086 - Drives, Storage & Blank Media > Network Storage
- 162063 - Uninterruptible Power Supplies (UPS)
- 51071 - Computer Components & Parts > Motherboards

**Use case:** "Show me all subcategories under Enterprise Networking"

#### 4. `get_item_details` - Deep Item Info
**What it does:** Get comprehensive listing information
**Returns:**
- Title, description, condition
- Current price, original price, discount
- Shipping cost, handling time, location
- Seller info (rating, feedback score, top-rated status)
- Item specifics (brand, model, specs)
- Photos (URLs)
- Listing end time
- Return policy
- Watch count (if available)

**Use case:** "Get full details on item 234567890"

## Phase 2: Price Intelligence

### 💰 Price Tracking Tools

#### 5. `track_price` - Add to Watchlist
**What it does:** Start monitoring an item's price
**Parameters:**
- `item_id` (required)
- `alert_threshold` - Alert when price drops below this
- `alert_percentage` - Alert on X% price drop
- `check_frequency` - How often to check (hourly, daily)
- `notes` - Personal notes about why tracking

**Database schema:**
```sql
CREATE TABLE tracked_items (
    item_id TEXT PRIMARY KEY,
    title TEXT,
    category TEXT,
    first_seen_price REAL,
    first_seen_date TEXT,
    alert_threshold REAL,
    alert_percentage REAL,
    check_frequency TEXT,
    notes TEXT,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT,
    price REAL,
    shipping_cost REAL,
    currency TEXT DEFAULT 'USD',
    condition TEXT,
    timestamp TEXT,
    FOREIGN KEY (item_id) REFERENCES tracked_items(item_id)
);
```

**Use case:** "Track item 234567890, alert me if it drops below $350 or by 15%"

#### 6. `get_price_history` - Historical Data
**What it does:** Show price changes over time
**Parameters:**
- `item_id` (required)
- `days` - Lookback period (default: 30)
- `include_stats` - Show min/max/avg/median

**Returns:**
```json
{
  "item_id": "234567890",
  "title": "Dell PowerEdge R720",
  "price_history": [
    {"date": "2026-02-09", "price": 449.99, "shipping": 0},
    {"date": "2026-02-08", "price": 449.99, "shipping": 0},
    {"date": "2026-02-07", "price": 479.99, "shipping": 0}
  ],
  "stats": {
    "current_price": 449.99,
    "lowest_price": 449.99,
    "highest_price": 479.99,
    "average_price": 459.99,
    "median_price": 449.99,
    "price_trend": "decreasing",
    "percent_change": -6.25
  }
}
```

#### 7. `list_tracked_items` - View Watchlist
**What it does:** Show all items being tracked
**Parameters:**
- `active_only` - Only show active tracking (default: true)
- `sort_by` - current_price, price_change, date_added

**Use case:** "Show me all items I'm tracking, sorted by biggest price drops"

#### 8. `untrack_price` - Stop Tracking
**What it does:** Remove item from watchlist (keeps historical data)
**Parameters:**
- `item_id` (required)
- `delete_history` - Permanently delete price data (default: false)

## Phase 3: Deal Detection & Market Intelligence

### 🎯 Deal Finding Tools

#### 9. `find_deals` - Below-Market-Value Finder
**What it does:** Find items priced lower than typical market value
**Parameters:**
- `keywords` (required)
- `discount_threshold` - Minimum % below average (default: 15%)
- `sample_size` - How many comparable items to analyze (default: 50)
- `condition` - Filter by condition
- `limit` - Max deals to return

**Algorithm:**
1. Search for `keywords`
2. Get last 50 sold/completed listings for price baseline
3. Calculate average/median market price
4. Find active listings X% below market
5. Score deals by: (discount % × seller rating × condition score)
6. Return top deals, ranked

**Returns:**
```json
{
  "keyword": "Dell R720",
  "market_analysis": {
    "sample_size": 50,
    "average_price": 485.00,
    "median_price": 475.00,
    "price_range": [350, 650]
  },
  "deals": [
    {
      "item_id": "123456",
      "title": "Dell PowerEdge R720 128GB RAM",
      "current_price": 399.99,
      "market_price": 485.00,
      "discount_amount": 85.01,
      "discount_percent": 17.5,
      "deal_score": 8.7,
      "condition": "Refurbished",
      "seller_rating": 99.2,
      "shipping": "Free",
      "time_left": "2d 4h"
    }
  ]
}
```

**Use case:** "Find Dell R720 servers at least 20% below market value"

#### 10. `get_market_value` - Price Research
**What it does:** Estimate fair market value for an item
**Parameters:**
- `keywords` - What to research
- `condition` - Specific condition
- `lookback_days` - Historical period (default: 90)

**Use case:** "What's the market value for a used Dell R720 with 128GB RAM?"

#### 11. `find_new_listings` - Fresh Listings Alert
**What it does:** Find recently listed items (catch deals early)
**Parameters:**
- `keywords` (required)
- `max_age_hours` - Only show listings newer than X hours (default: 24)
- `filters` - Price, condition, etc.

**Use case:** "Show me Dell R720 servers listed in the last 6 hours under $450"

#### 12. `find_ending_soon` - Auction Sniper Helper
**What it does:** Find auctions ending soon with low bids
**Parameters:**
- `keywords` (required)
- `hours_remaining` - Max time left (default: 24)
- `max_current_bid` - Only show if current bid is below this
- `include_buy_now` - Include auctions with Buy It Now option

**Use case:** "Show me server auctions ending in the next 12 hours with current bid under $300"

## Phase 4: Purchasing (⚠️ High Risk - Requires Careful Implementation)

### 🛒 Transaction Tools

#### 13. `place_bid` - Bid on Auction
**What it does:** Place a bid on an auction listing
**Parameters:**
- `item_id` (required)
- `bid_amount` (required)
- `confirm` - Must be explicitly true (safety)

**Requirements:**
- eBay Trading API access (separate from Finding API)
- OAuth 2.0 user authentication
- User must grant explicit permission
- eBay account must have payment method on file
- Dry-run mode for testing

**Safety features:**
- Confirmation prompt with item details
- Maximum bid limit (user-configurable)
- Audit log of all bid attempts
- Can't bid on own listings

**Use case:** "Bid $450 on item 234567890 (with confirmation)"

#### 14. `buy_it_now` - Purchase Fixed Price Item
**What it does:** Immediately purchase a Buy It Now listing
**Parameters:**
- `item_id` (required)
- `quantity` (default: 1)
- `confirm` - Must be explicitly true

**Safety features:**
- Price confirmation before purchase
- Spending limit checks
- Review seller rating before proceeding
- Audit log
- Cooldown period between purchases

**Use case:** "Buy item 234567890 for $399.99 (with confirmation)"

#### 15. `make_offer` - Send Best Offer
**What it does:** Submit a best offer on eligible listings
**Parameters:**
- `item_id` (required)
- `offer_amount` (required)
- `message` - Optional message to seller
- `confirm` - Must be true

**Use case:** "Offer $350 on item 234567890 with message 'Can you include rails?'"

#### 16. `get_purchase_history` - Transaction Log
**What it does:** View items purchased through MCP
**Returns:** List of purchases with dates, amounts, status

## Phase 5: Advanced Features (Future)

### 📊 Analytics & Automation

#### 17. `create_saved_search` - Persistent Search
**What it does:** Save search criteria for recurring use
**Parameters:**
- `name` - Search name
- `filters` - All search parameters
- `alert_on_new` - Get notified of new matching listings
- `run_frequency` - How often to check (hourly, daily, weekly)

**Use case:** "Save this search as 'Homelab Servers Under $500' and check daily"

#### 18. `compare_items` - Side-by-Side Comparison
**What it does:** Compare multiple listings
**Parameters:**
- `item_ids` - List of items to compare
- `comparison_fields` - Price, specs, seller rating, etc.

#### 19. `get_seller_info` - Seller Research
**What it does:** Deep dive into seller's reputation
**Parameters:**
- `seller_username` (required)

**Returns:** Feedback score, ratings, active listings, specialties

#### 20. `bulk_track` - Track Multiple Items
**What it does:** Add many items to watchlist at once
**Parameters:**
- `item_ids` - List of item IDs
- `alert_threshold` - Apply to all

**Use case:** "Track all these 10 server listings, alert at $400"

---

## Purchasing Discussion: Should We Enable It?

### ⚠️ Security & Safety Concerns

**Pros:**
✅ Complete automation - Find → Track → Buy
✅ Quick deals - Grab underpriced items instantly
✅ Auction sniping - Bid at the last second
✅ Time savings - No manual intervention needed

**Cons:**
❌ **Financial risk** - Bugs could cost real money
❌ **Authentication complexity** - OAuth 2.0, token refresh, secure storage
❌ **Legal liability** - Binding contracts made automatically
❌ **Account security** - eBay credentials in environment
❌ **No undo** - Can't easily reverse purchases
❌ **Testing difficulty** - Need sandbox environment
❌ **Potential for abuse** - AI making purchases without full user understanding

### My Recommendation: Phased Approach

**Phase 1-3 (Safe):** Search, tracking, deal detection - **BUILD THIS FIRST**
- Zero financial risk
- Read-only operations
- Can test freely
- Immediate value

**Phase 4 (Risky):** Purchasing - **OPTIONAL, REQUIRES:**
1. **Explicit user opt-in** - Separate configuration flag
2. **Spending limits** - Daily/per-item maximums
3. **Confirmation prompts** - Never auto-purchase without review
4. **Dry-run mode** - Test without real transactions
5. **Audit logging** - Track every purchase attempt
6. **Insurance/safeguards** - Way to quickly cancel or dispute

### Alternative: Notification + Manual Purchase

Instead of auto-purchasing, MCP could:
1. Find deal (`find_deals`)
2. Alert you via Matrix notification
3. Provide direct eBay link
4. You manually purchase on eBay (safe)

**This gives you:**
- Speed (immediate notification)
- Safety (you click "buy")
- Control (review before committing)

---

## Recommended MVP (Start Here)

For homelab deal hunting, I recommend starting with:

**Core Search:**
1. `search_ebay` - Basic search
2. `search_ebay_advanced` - Power search
3. `get_item_details` - Item info

**Price Intelligence:**
4. `track_price` - Start tracking
5. `get_price_history` - View trends
6. `list_tracked_items` - Watchlist

**Deal Detection:**
7. `find_deals` - Below-market finder
8. `find_new_listings` - Fresh deals

**Skip purchasing for now.** Get search + tracking working first, then decide if auto-purchasing is worth the risk.

---

## What do you think?

1. Does this feature list cover your needs?
2. Any tools you'd add/remove?
3. Should we include purchasing, or stick with notification + manual buy?
4. Want me to start implementing the MVP (tools 1-8)?
