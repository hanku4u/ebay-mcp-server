# TODO

## Immediate Next Steps

### 1. eBay API Integration
- [ ] Add `ebaysdk-python` dependency to pyproject.toml
- [ ] Implement `_search_ebay()` using eBay Finding API
  - [ ] Build API request with search filters
  - [ ] Parse response and format results
  - [ ] Handle pagination
  - [ ] Error handling for API failures
- [ ] Implement `_get_item_details()` using eBay Shopping API
  - [ ] Get comprehensive item data
  - [ ] Include shipping costs
  - [ ] Parse seller information

### 2. Price Tracking System
- [ ] Design database schema (SQLite)
  - [ ] `tracked_items` table (item_id, title, category, first_price, alert_threshold)
  - [ ] `price_history` table (item_id, price, timestamp, shipping_cost)
- [ ] Implement `_track_price()`
  - [ ] Add item to database
  - [ ] Initial price capture
- [ ] Implement `_get_price_history()`
  - [ ] Query database for historical prices
  - [ ] Format response with trend analysis
- [ ] Create background price monitoring service
  - [ ] Periodic price checks for tracked items
  - [ ] Alert generation when price drops

### 3. Deal Detection Algorithm
- [ ] Implement `_find_deals()`
  - [ ] Search eBay for items
  - [ ] Cross-reference with historical price data
  - [ ] Calculate average/median prices
  - [ ] Identify items below threshold
  - [ ] Rank by deal quality (price, condition, seller rating)

### 4. Testing
- [ ] Add unit tests for each tool
- [ ] Add integration tests with eBay sandbox API
- [ ] Test error handling (network failures, invalid credentials, etc.)
- [ ] Mock API responses for CI/CD

### 5. Documentation
- [ ] Update README with actual usage examples
- [ ] Add configuration guide with screenshots
- [ ] Document eBay category IDs for common homelab items
  - Computer Servers: 175673
  - Enterprise Networking: 175698
  - Network Storage: 182086
- [ ] Add troubleshooting section

### 6. OpenClaw Integration
- [ ] Document OpenClaw cron job setup
- [ ] Create example recurring search configurations
- [ ] Test with OpenClaw isolated sessions
- [ ] Add output formatting optimized for chat delivery

## Future Enhancements

### Phase 2
- [ ] Web UI for managing tracked items
- [ ] Email/notification alerts for price drops
- [ ] Export tracking data to CSV
- [ ] Support for saved searches
- [ ] Compare prices across multiple marketplaces

### Phase 3
- [ ] Machine learning for deal quality prediction
- [ ] Historical trend visualization
- [ ] Seller reputation analysis
- [ ] Automated bidding assistance (with user approval)

## Notes
- Focus on homelab equipment categories first (servers, networking, storage)
- Prioritize reliability over features - recurring searches need to be stable
- Keep responses concise for chat delivery
