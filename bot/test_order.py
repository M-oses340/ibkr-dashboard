#!/usr/bin/env python3
"""
Simple test script to place an order on IBKR
"""

import requests
import os

# Disable SSL warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
IBKR_API_URL = "https://localhost:5055/v1/api"
ACCOUNT_ID = os.environ.get('IBKR_ACCOUNT_ID', 'DUP158699')

def get_btc_price():
    """Get current BTC price"""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    return float(response.json()['price'])

def place_test_order():
    """Place a test market order for 1 share of AAPL"""
    
    print("=" * 60)
    print("Testing IBKR Order Placement")
    print("=" * 60)
    
    # Get BTC price first
    btc_price = get_btc_price()
    print(f"\nCurrent BTC Price: ${btc_price:,.2f}")
    
    # Order details
    order_data = {
        "orders": [{
            "conid": 265598,  # AAPL
            "orderType": "MKT",  # Market order
            "quantity": 1,
            "side": "BUY",
            "tif": "DAY"
        }]
    }
    
    print(f"\nPlacing order:")
    print(f"  Stock: AAPL (Apple)")
    print(f"  Side: BUY")
    print(f"  Quantity: 1 share")
    print(f"  Order Type: Market")
    print(f"  Account: {ACCOUNT_ID}")
    
    try:
        url = f"{IBKR_API_URL}/iserver/account/{ACCOUNT_ID}/orders"
        response = requests.post(url, json=order_data, verify=False)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ Order placed successfully!")
        else:
            print("\n❌ Order failed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    print("\n⚠️  This will place a REAL order on your demo account")
    place_test_order()
