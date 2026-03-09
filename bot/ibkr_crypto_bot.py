#!/usr/bin/env python3
"""
IBKR Crypto Trading Bot
Monitors crypto prices from Binance and trades crypto on IBKR
"""

import requests
import time
import os
from datetime import datetime

# Disable SSL warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
IBKR_API_URL = "https://localhost:5055/v1/api"
ACCOUNT_ID = os.environ.get('IBKR_ACCOUNT_ID', 'DUP158699')

# IBKR Crypto Contract IDs (you'll need to find these for your specific crypto)
# These are examples - you need to search for the actual contract IDs
CRYPTO_CONTRACTS = {
    'BTC': None,  # Bitcoin futures or crypto product
    'ETH': None,  # Ethereum futures or crypto product
}


def get_binance_price(symbol="BTCUSDT"):
    """Get current crypto price from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)
        return float(response.json()['price'])
    except Exception as e:
        print(f"Error fetching Binance price: {e}")
        return None


def get_binance_24h_stats(symbol="BTCUSDT"):
    """Get 24h statistics from Binance"""
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        return {
            'price': float(data['lastPrice']),
            'high_24h': float(data['highPrice']),
            'low_24h': float(data['lowPrice']),
            'change_percent': float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return None


def search_ibkr_crypto(symbol):
    """Search for crypto contracts on IBKR"""
    try:
        url = f"{IBKR_API_URL}/iserver/secdef/search?symbol={symbol}&name=true"
        response = requests.get(url, verify=False)
        results = response.json()
        
        print(f"\nSearch results for '{symbol}':")
        for i, result in enumerate(results[:10], 1):
            print(f"{i}. {result.get('description', 'N/A')} - "
                  f"Type: {result.get('assetClass', 'N/A')} - "
                  f"ConID: {result.get('conid', 'N/A')}")
        
        return results
    except Exception as e:
        print(f"Error searching IBKR: {e}")
        return []


def get_ibkr_positions():
    """Get current positions from IBKR"""
    try:
        url = f"{IBKR_API_URL}/portfolio/{ACCOUNT_ID}/positions/0"
        response = requests.get(url, verify=False)
        
        if response.content:
            return response.json()
        return []
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []


def display_crypto_positions():
    """Display current crypto positions on IBKR"""
    positions = get_ibkr_positions()
    
    print("\n" + "=" * 70)
    print("YOUR IBKR CRYPTO POSITIONS")
    print("=" * 70)
    
    if not positions:
        print("No positions found")
        return
    
    crypto_positions = []
    for pos in positions:
        # Filter for crypto-related positions
        asset_class = pos.get('assetClass', '')
        ticker = pos.get('ticker', '')
        
        # Look for crypto keywords
        if any(crypto in ticker.upper() for crypto in ['BTC', 'ETH', 'CRYPTO', 'COIN']):
            crypto_positions.append(pos)
    
    if not crypto_positions:
        print("No crypto positions found")
        print("\nAll positions:")
        for pos in positions:
            print(f"  • {pos.get('contractDesc', 'N/A')} - "
                  f"Qty: {pos.get('position', 0)} - "
                  f"Value: ${pos.get('mktValue', 0):,.2f}")
    else:
        for pos in crypto_positions:
            print(f"\n{pos.get('contractDesc', 'N/A')}")
            print(f"  Ticker: {pos.get('ticker', 'N/A')}")
            print(f"  Quantity: {pos.get('position', 0)}")
            print(f"  Avg Price: ${pos.get('avgPrice', 0):,.2f}")
            print(f"  Market Value: ${pos.get('mktValue', 0):,.2f}")
            print(f"  P&L: ${pos.get('unrealizedPnl', 0):,.2f}")
    
    print("=" * 70)


def place_crypto_order(conid, side, quantity, order_type="MKT"):
    """Place a crypto order on IBKR"""
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
        
        print(f"\nOrder Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error placing order: {e}")
        return None


def main():
    print("\n" + "=" * 70)
    print("IBKR CRYPTO TRADING BOT")
    print("=" * 70)
    
    # Show current positions
    display_crypto_positions()
    
    # Get BTC price from Binance for reference
    btc_stats = get_binance_24h_stats("BTCUSDT")
    if btc_stats:
        print(f"\n📊 BTC Price (Binance): ${btc_stats['price']:,.2f}")
        print(f"📈 24h Change: {btc_stats['change_percent']:+.2f}%")
    
    # Search for crypto on IBKR
    print("\n" + "=" * 70)
    print("Searching for crypto products on IBKR...")
    print("=" * 70)
    
    search_terms = ['BTC', 'BITCOIN', 'CRYPTO']
    for term in search_terms:
        print(f"\nSearching for: {term}")
        search_ibkr_crypto(term)
        time.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 70)
    print("\nTo trade crypto on IBKR, you need the contract ID (conid).")
    print("Use the search results above to find your crypto product.")
    print("\nIBKR offers:")
    print("  • Crypto futures (CME)")
    print("  • Crypto CFDs (in some regions)")
    print("  • Crypto-related stocks/ETFs")
    print("=" * 70)


if __name__ == "__main__":
    main()
