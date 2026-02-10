"""Database operations for price tracking."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any


class PriceTrackingDB:
    """SQLite database for price tracking and history."""
    
    def __init__(self, db_path: str = "ebay_tracking.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracked_items (
                    item_id TEXT PRIMARY KEY,
                    title TEXT,
                    category TEXT,
                    url TEXT,
                    first_seen_price REAL,
                    first_seen_date TEXT,
                    alert_threshold REAL,
                    alert_percentage REAL,
                    check_frequency TEXT DEFAULT 'daily',
                    notes TEXT,
                    active INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id TEXT,
                    price REAL,
                    shipping_cost REAL,
                    currency TEXT DEFAULT 'USD',
                    condition TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES tracked_items(item_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_item_id 
                ON price_history(item_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_timestamp 
                ON price_history(timestamp)
            """)
            
            conn.commit()
    
    def track_item(
        self,
        item_id: str,
        title: str,
        current_price: float,
        url: str = "",
        category: str = "",
        alert_threshold: Optional[float] = None,
        alert_percentage: Optional[float] = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Add an item to tracking watchlist."""
        with sqlite3.connect(self.db_path) as conn:
            now = datetime.utcnow().isoformat()
            
            # Insert or update tracked item
            conn.execute("""
                INSERT OR REPLACE INTO tracked_items 
                (item_id, title, category, url, first_seen_price, first_seen_date,
                 alert_threshold, alert_percentage, notes, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (item_id, title, category, url, current_price, now,
                  alert_threshold, alert_percentage, notes))
            
            # Add initial price to history
            conn.execute("""
                INSERT INTO price_history (item_id, price, shipping_cost, timestamp)
                VALUES (?, ?, 0, ?)
            """, (item_id, current_price, now))
            
            conn.commit()
        
        return {
            "status": "success",
            "item_id": item_id,
            "title": title,
            "first_price": current_price,
            "alert_threshold": alert_threshold,
            "alert_percentage": alert_percentage
        }
    
    def untrack_item(self, item_id: str, delete_history: bool = False) -> Dict[str, Any]:
        """Remove item from tracking (optionally delete history)."""
        with sqlite3.connect(self.db_path) as conn:
            if delete_history:
                conn.execute("DELETE FROM price_history WHERE item_id = ?", (item_id,))
                conn.execute("DELETE FROM tracked_items WHERE item_id = ?", (item_id,))
                message = "Item and all history deleted"
            else:
                conn.execute("UPDATE tracked_items SET active = 0 WHERE item_id = ?", (item_id,))
                message = "Item marked inactive (history preserved)"
            
            conn.commit()
        
        return {
            "status": "success",
            "item_id": item_id,
            "message": message
        }
    
    def add_price_point(
        self,
        item_id: str,
        price: float,
        shipping_cost: float = 0,
        condition: str = ""
    ) -> None:
        """Add a new price data point for an item."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO price_history (item_id, price, shipping_cost, condition)
                VALUES (?, ?, ?, ?)
            """, (item_id, price, shipping_cost, condition))
            conn.commit()
    
    def get_price_history(self, item_id: str, days: int = 30) -> Dict[str, Any]:
        """Get price history for an item."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get item info
            item = conn.execute("""
                SELECT * FROM tracked_items WHERE item_id = ?
            """, (item_id,)).fetchone()
            
            if not item:
                return {
                    "status": "error",
                    "message": "Item not found in tracking database"
                }
            
            # Get price history
            history = conn.execute("""
                SELECT price, shipping_cost, condition, timestamp
                FROM price_history
                WHERE item_id = ?
                AND datetime(timestamp) >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp ASC
            """, (item_id, days)).fetchall()
            
            if not history:
                return {
                    "status": "success",
                    "item_id": item_id,
                    "title": item["title"],
                    "message": "No price history available for this period"
                }
            
            # Calculate statistics
            prices = [row["price"] for row in history]
            current_price = prices[-1]
            lowest_price = min(prices)
            highest_price = max(prices)
            average_price = sum(prices) / len(prices)
            median_price = sorted(prices)[len(prices) // 2]
            
            # Determine trend
            if len(prices) >= 2:
                price_change = ((current_price - prices[0]) / prices[0]) * 100
                if price_change < -5:
                    trend = "decreasing"
                elif price_change > 5:
                    trend = "increasing"
                else:
                    trend = "stable"
            else:
                price_change = 0
                trend = "unknown"
            
            return {
                "status": "success",
                "item_id": item_id,
                "title": item["title"],
                "url": item["url"],
                "price_history": [
                    {
                        "date": row["timestamp"][:10],
                        "price": row["price"],
                        "shipping": row["shipping_cost"],
                        "condition": row["condition"]
                    }
                    for row in history
                ],
                "stats": {
                    "data_points": len(prices),
                    "current_price": round(current_price, 2),
                    "lowest_price": round(lowest_price, 2),
                    "highest_price": round(highest_price, 2),
                    "average_price": round(average_price, 2),
                    "median_price": round(median_price, 2),
                    "price_trend": trend,
                    "percent_change": round(price_change, 2)
                }
            }
    
    def list_tracked_items(self, active_only: bool = True, sort_by: str = "date_added") -> List[Dict[str, Any]]:
        """List all tracked items."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM tracked_items"
            if active_only:
                query += " WHERE active = 1"
            
            # Apply sorting
            if sort_by == "current_price":
                query += " ORDER BY first_seen_price ASC"
            elif sort_by == "date_added":
                query += " ORDER BY created_at DESC"
            else:
                query += " ORDER BY created_at DESC"
            
            items = conn.execute(query).fetchall()
            
            result = []
            for item in items:
                # Get latest price
                latest_price = conn.execute("""
                    SELECT price, timestamp FROM price_history
                    WHERE item_id = ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (item["item_id"],)).fetchone()
                
                result.append({
                    "item_id": item["item_id"],
                    "title": item["title"],
                    "category": item["category"],
                    "url": item["url"],
                    "first_price": item["first_seen_price"],
                    "current_price": latest_price["price"] if latest_price else item["first_seen_price"],
                    "alert_threshold": item["alert_threshold"],
                    "alert_percentage": item["alert_percentage"],
                    "notes": item["notes"],
                    "tracking_since": item["created_at"][:10]
                })
            
            return result
    
    def get_items_needing_check(self) -> List[str]:
        """Get list of item IDs that need price checking."""
        with sqlite3.connect(self.db_path) as conn:
            # For now, return all active items
            # TODO: Implement smart checking based on check_frequency
            items = conn.execute("""
                SELECT item_id FROM tracked_items WHERE active = 1
            """).fetchall()
            
            return [item[0] for item in items]
