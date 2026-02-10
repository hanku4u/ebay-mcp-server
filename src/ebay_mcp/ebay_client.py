"""eBay API client for Finding and Shopping APIs."""

import os
from typing import Dict, List, Optional, Any
from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping
from ebaysdk.exception import ConnectionError


class EbayAPIClient:
    """Client for eBay Finding and Shopping APIs."""
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        cert_id: Optional[str] = None,
        dev_id: Optional[str] = None,
        domain: str = "svcs.ebay.com"
    ):
        """
        Initialize eBay API client.
        
        Args:
            app_id: eBay App ID (or uses EBAY_APP_ID env var)
            cert_id: eBay Cert ID (or uses EBAY_CERT_ID env var)
            dev_id: eBay Dev ID (or uses EBAY_DEV_ID env var)
            domain: API domain (default: production, use svcs.sandbox.ebay.com for testing)
        """
        self.app_id = app_id or os.getenv("EBAY_APP_ID")
        self.cert_id = cert_id or os.getenv("EBAY_CERT_ID")
        self.dev_id = dev_id or os.getenv("EBAY_DEV_ID")
        self.domain = domain
        
        if not self.app_id:
            raise ValueError("eBay App ID required (set EBAY_APP_ID environment variable)")
        
        self.finding_api = Finding(appid=self.app_id, config_file=None, domain=domain)
        self.shopping_api = Shopping(appid=self.app_id, config_file=None, domain=domain)
    
    def search(
        self,
        keywords: str,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        condition: Optional[str] = None,
        category_id: Optional[str] = None,
        sort_by: str = "BestMatch",
        limit: int = 20,
        item_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search eBay listings using Finding API.
        
        Args:
            keywords: Search keywords
            max_price: Maximum price filter
            min_price: Minimum price filter
            condition: Item condition (New, Used, Refurbished, etc.)
            category_id: eBay category ID
            sort_by: Sort order
            limit: Number of results
            item_filter: Additional filters (for advanced search)
        
        Returns:
            Search results dictionary
        """
        try:
            # Build item filters
            filters = []
            
            if max_price:
                filters.append({
                    'name': 'MaxPrice',
                    'value': str(max_price),
                    'paramName': 'Currency',
                    'paramValue': 'USD'
                })
            
            if min_price:
                filters.append({
                    'name': 'MinPrice',
                    'value': str(min_price),
                    'paramName': 'Currency',
                    'paramValue': 'USD'
                })
            
            if condition:
                # Map condition names to eBay condition IDs
                condition_map = {
                    'New': '1000',
                    'Used': '3000',
                    'Refurbished': '2000',
                    'For parts or not working': '7000'
                }
                condition_id = condition_map.get(condition, condition)
                filters.append({
                    'name': 'Condition',
                    'value': condition_id
                })
            
            # Add custom filters from item_filter parameter
            if item_filter:
                for filter_name, filter_value in item_filter.items():
                    filters.append({
                        'name': filter_name,
                        'value': str(filter_value)
                    })
            
            # Build request
            request = {
                'keywords': keywords,
                'sortOrder': sort_by,
                'paginationInput': {
                    'entriesPerPage': limit,
                    'pageNumber': 1
                }
            }
            
            if filters:
                request['itemFilter'] = filters
            
            if category_id:
                request['categoryId'] = category_id
            
            # Execute search
            response = self.finding_api.execute('findItemsAdvanced', request)
            
            # Parse results
            search_result = response.dict()
            items = []
            
            if 'searchResult' in search_result and 'item' in search_result['searchResult']:
                for item in search_result['searchResult']['item']:
                    items.append({
                        'item_id': item.get('itemId', ''),
                        'title': item.get('title', ''),
                        'url': item.get('viewItemURL', ''),
                        'price': float(item['sellingStatus']['currentPrice']['value']) if 'sellingStatus' in item else 0,
                        'currency': item['sellingStatus']['currentPrice'].get('_currencyId', 'USD') if 'sellingStatus' in item else 'USD',
                        'condition': item.get('condition', {}).get('conditionDisplayName', 'Unknown'),
                        'location': item.get('location', ''),
                        'shipping_cost': float(item['shippingInfo']['shippingServiceCost']['value']) if 'shippingInfo' in item and 'shippingServiceCost' in item['shippingInfo'] else 0,
                        'shipping_type': item.get('shippingInfo', {}).get('shippingType', ''),
                        'image_url': item.get('galleryURL', ''),
                        'listing_type': item.get('listingInfo', {}).get('listingType', ''),
                        'time_left': item.get('sellingStatus', {}).get('timeLeft', ''),
                        'end_time': item.get('listingInfo', {}).get('endTime', ''),
                        'watch_count': item.get('listingInfo', {}).get('watchCount', 0)
                    })
            
            return {
                'status': 'success',
                'query': keywords,
                'filters': {
                    'max_price': max_price,
                    'min_price': min_price,
                    'condition': condition,
                    'category_id': category_id,
                    'sort_by': sort_by
                },
                'results_count': len(items),
                'items': items
            }
        
        except ConnectionError as e:
            return {
                'status': 'error',
                'message': f"eBay API error: {str(e)}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Unexpected error: {str(e)}"
            }
    
    def get_item_details(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific item using Shopping API.
        
        Args:
            item_id: eBay item ID
        
        Returns:
            Detailed item information
        """
        try:
            response = self.shopping_api.execute('GetSingleItem', {
                'ItemID': item_id,
                'IncludeSelector': 'Details,Description,ItemSpecifics,ShippingCosts'
            })
            
            item_dict = response.dict()
            item = item_dict.get('Item', {})
            
            return {
                'status': 'success',
                'item_id': item_id,
                'title': item.get('Title', ''),
                'description': item.get('Description', ''),
                'condition': item.get('ConditionDisplayName', 'Unknown'),
                'condition_id': item.get('ConditionID', ''),
                'price': {
                    'current': float(item['CurrentPrice']['Value']) if 'CurrentPrice' in item else 0,
                    'currency': item.get('CurrentPrice', {}).get('CurrencyID', 'USD'),
                    'converted': float(item['ConvertedCurrentPrice']['Value']) if 'ConvertedCurrentPrice' in item else 0
                },
                'location': item.get('Location', ''),
                'country': item.get('Country', ''),
                'shipping': {
                    'cost': float(item['ShippingCostSummary']['ShippingServiceCost']['Value']) if 'ShippingCostSummary' in item else 0,
                    'type': item.get('ShippingCostSummary', {}).get('ShippingType', ''),
                    'handling_time': item.get('HandlingTime', '')
                },
                'seller': {
                    'username': item.get('Seller', {}).get('UserID', ''),
                    'feedback_score': item.get('Seller', {}).get('FeedbackScore', 0),
                    'positive_percentage': item.get('Seller', {}).get('PositiveFeedbackPercent', 0),
                    'top_rated': item.get('Seller', {}).get('TopRatedSeller', False)
                },
                'listing_info': {
                    'listing_type': item.get('ListingType', ''),
                    'start_time': item.get('StartTime', ''),
                    'end_time': item.get('EndTime', ''),
                    'time_left': item.get('TimeLeft', ''),
                    'view_count': item.get('HitCount', 0)
                },
                'urls': {
                    'view_item': item.get('ViewItemURLForNaturalSearch', ''),
                    'gallery': item.get('GalleryURL', ''),
                    'picture_urls': item.get('PictureURL', [])
                },
                'return_policy': item.get('ReturnPolicy', {}),
                'item_specifics': item.get('ItemSpecifics', {})
            }
        
        except ConnectionError as e:
            return {
                'status': 'error',
                'message': f"eBay API error: {str(e)}"
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Unexpected error: {str(e)}"
            }
    
    def get_completed_listings(
        self,
        keywords: str,
        days: int = 90,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get completed/sold listings for market value analysis.
        
        Args:
            keywords: Search keywords
            days: Lookback period in days
            limit: Number of results
        
        Returns:
            List of sold items with prices
        """
        try:
            response = self.finding_api.execute('findCompletedItems', {
                'keywords': keywords,
                'itemFilter': [
                    {'name': 'SoldItemsOnly', 'value': 'true'}
                ],
                'sortOrder': 'EndTimeSoonest',
                'paginationInput': {
                    'entriesPerPage': limit,
                    'pageNumber': 1
                }
            })
            
            search_result = response.dict()
            items = []
            
            if 'searchResult' in search_result and 'item' in search_result['searchResult']:
                for item in search_result['searchResult']['item']:
                    if 'sellingStatus' in item and 'currentPrice' in item['sellingStatus']:
                        items.append({
                            'item_id': item.get('itemId', ''),
                            'title': item.get('title', ''),
                            'price': float(item['sellingStatus']['currentPrice']['value']),
                            'condition': item.get('condition', {}).get('conditionDisplayName', 'Unknown'),
                            'sold_date': item.get('listingInfo', {}).get('endTime', '')
                        })
            
            return items
        
        except Exception as e:
            return []
