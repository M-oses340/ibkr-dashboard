#!/usr/bin/env python3
"""
Test BTC order placement with cashQty
"""

import requests
import os

# Disable SSL warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
IBKR_API_URL = "https://localhost:5055/v1/api"
ACCOUNT_ID = os.environ.get('IBKR_ACCOUNT_ID', 'DUP158699')
BTC_CONID = 479624278

def get_btc_price():
    """Get current BTC price"""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    response = requests.get(url)
    return float(response.json()['price'])

def test_btc_order():
    """Test placing a BTC order with cashQty"""
    
    print("=" * 60)
    print("Testing BTC Order Placement (cashQty)")
    print("=" * 60)
    
    # Get BTC price
    btc_price = get_btc_price()
    print(f"\nCurrent BTC Price: ${btc_price:,.2f}")
    
    # Calculate cash amount for 0.1 BTC
    trade_btc = 0.1
    trade_cash = round(trade_btc * btc_price, 2)  # Round to 2 decimals
    
    print(f"Trade Amount: {trade_btc} BTC = ${trade_cash:.2f}")
    
    # Order details using cashQty
    order_data = {
        "orders": [{
            "conid": BTC_CONID,
            "orderType": "MKT",
            "cashQty": trade_cash,  # Use cashQty for crypto
            "side": "BUY",
            "tif": "IOC"  # Immediate or Cancel (required for crypto)
        }]
    }
    
    print(f"\nPlacing order:")
    print(f"  Asset: BTC (Bitcoin)")
    print(f"  Side: BUY")
    print(f"  Cash Amount: ${trade_cash:.2f}")
    print(f"  Approx BTC: {trade_btc}")
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
    print("⚠️  Order: BUY ~$6,800 worth of BTC (0.1 BTC)")
    
    choice = input("\nProceed? (yes/no): ").lower()
    if choice == 'yes':
        test_btc_order()
    else:
        print("Exiting...")
