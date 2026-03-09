#!/usr/bin/env python3
"""
Simple BTC Price Monitor Bot
Fetches Bitcoin price from Binance and displays it
"""

import requests
import time
from datetime import datetime


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


def get_btc_24h_stats():
    """Fetch 24h statistics for BTC"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        response = requests.get(url)
        data = response.json()
        return {
            'price': float(data['lastPrice']),
            'high_24h': float(data['highPrice']),
            'low_24h': float(data['lowPrice']),
            'volume_24h': float(data['volume']),
            'price_change_24h': float(data['priceChange']),
            'price_change_percent': float(data['priceChangePercent'])
        }
    except Exception as e:
        print(f"Error fetching BTC stats: {e}")
        return None


def monitor_btc(interval=10):
    """
    Monitor BTC price continuously
    
    Args:
        interval: Time in seconds between price checks
    """
    print("=" * 60)
    print("BTC Price Monitor - Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        while True:
            stats = get_btc_24h_stats()
            
            if stats:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"\n[{timestamp}]")
                print(f"BTC Price: ${stats['price']:,.2f}")
                print(f"24h High:  ${stats['high_24h']:,.2f}")
                print(f"24h Low:   ${stats['low_24h']:,.2f}")
                print(f"24h Change: {stats['price_change_percent']:+.2f}%")
                print(f"24h Volume: {stats['volume_24h']:,.2f} BTC")
                print("-" * 60)
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")


if __name__ == "__main__":
    # Monitor BTC price every 10 seconds
    monitor_btc(interval=10)
