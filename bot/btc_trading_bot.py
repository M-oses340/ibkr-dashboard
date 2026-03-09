#!/usr/bin/env python3
"""
BTC Trading Bot
Monitors BTC price and places trades on IBKR based on price movements
"""

import requests
import time
import os
from datetime import datetime

# Disable SSL warnings for localhost
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
IBKR_API_URL = "https://localhost:5055/v1/api"
ACCOUNT_ID = os.environ.get('IBKR_ACCOUNT_ID', 'DUP158699')

# Trading parameters
BTC_THRESHOLD_UP = 68000  # If BTC goes above this, buy stocks
BTC_THRESHOLD_DOWN = 66000  # If BTC goes below this, sell stocks
STOCK_CONID = 265598  # Apple (AAPL) contract ID
TRADE_QUANTITY = 1  # Number of shares to trade


def get_btc_price():
    """Fetch current BTC price from Binance"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Error fetching BTC price: {e}")
        return None


def get_ibkr_positions():
    """Get current positions from IBKR"""
    try:
        url = f"{IBKR_API_URL}/portfolio/{ACCOUNT_ID}/positions/0"
        response = requests.get(url, verify=False)
        
        if response.content:
            positions = response.json()
            return positions
        return []
    except Exception as e:
        print(f"Error fetching IBKR positions: {e}")
        return []


def get_stock_position(conid):
    """Check if we have a position in a specific stock"""
    positions = get_ibkr_positions()
    
    for position in positions:
        if position.get('conid') == conid:
            return {
                'quantity': position.get('position', 0),
                'avgPrice': position.get('avgPrice', 0),
                'marketValue': position.get('mktValue', 0)
            }
    return None


def place_order(conid, side, quantity, order_type="MKT"):
    """
    Place an order on IBKR
    
    Args:
        conid: Contract ID
        side: "BUY" or "SELL"
        quantity: Number of shares
        order_type: "MKT" for market order, "LMT" for limit order
    """
    try:
        data = {
            "orders": [{
                "conid": conid,
                "orderType": order_type,
                "quantity": quantity,
                "side": side,
                "tif": "DAY"
            }]
        }
        
        url = f"{IBKR_API_URL}/iserver/account/{ACCOUNT_ID}/orders"
        response = requests.post(url, json=data, verify=False)
        
        print(f"Order response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error placing order: {e}")
        return None


def trading_logic(btc_price):
    """
    Main trading logic based on BTC price
    
    Strategy:
    - If BTC > $68,000 and we don't have AAPL, BUY
    - If BTC < $66,000 and we have AAPL, SELL
    """
    
    # Check current position
    position = get_stock_position(STOCK_CONID)
    has_position = position and position['quantity'] > 0
    
    print(f"\nCurrent AAPL Position: {position['quantity'] if position else 0} shares")
    
    # Trading decisions
    if btc_price > BTC_THRESHOLD_UP and not has_position:
        print(f"🚀 BTC above ${BTC_THRESHOLD_UP:,} - BUYING {TRADE_QUANTITY} AAPL")
        place_order(STOCK_CONID, "BUY", TRADE_QUANTITY)
        
    elif btc_price < BTC_THRESHOLD_DOWN and has_position:
        print(f"📉 BTC below ${BTC_THRESHOLD_DOWN:,} - SELLING {position['quantity']} AAPL")
        place_order(STOCK_CONID, "SELL", int(position['quantity']))
        
    else:
        print(f"⏸️  No action - BTC at ${btc_price:,.2f} (waiting for signal)")


def run_bot(interval=30):
    """
    Run the trading bot
    
    Args:
        interval: Time in seconds between checks
    """
    print("=" * 70)
    print("BTC Trading Bot - Press Ctrl+C to stop")
    print("=" * 70)
    print(f"Strategy:")
    print(f"  - BUY AAPL when BTC > ${BTC_THRESHOLD_UP:,}")
    print(f"  - SELL AAPL when BTC < ${BTC_THRESHOLD_DOWN:,}")
    print(f"  - Trade quantity: {TRADE_QUANTITY} shares")
    print("=" * 70)
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}]")
            
            # Get BTC price
            btc_price = get_btc_price()
            
            if btc_price:
                print(f"BTC Price: ${btc_price:,.2f}")
                
                # Execute trading logic
                trading_logic(btc_price)
            
            print("-" * 70)
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")


if __name__ == "__main__":
    # Make sure IBKR Gateway is running and authenticated
    print("\n⚠️  IMPORTANT: Make sure you're logged into IBKR Gateway at https://localhost:5055")
    print("⚠️  This bot will place REAL orders on your account!")
    
    input("\nPress Enter to start the bot (or Ctrl+C to cancel)...")
    
    # Run bot - checks every 30 seconds
    run_bot(interval=30)
