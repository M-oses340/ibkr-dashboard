#!/usr/bin/env python3
"""
Fast Market Data Fetcher
Uses Finnhub for real-time stock data (much faster than yfinance)
"""

import requests
import time

# Get free API key from: https://finnhub.io/register
FINNHUB_API_KEY = "demo"  # Replace with your key

class FastDataFetcher:
    """Fast real-time market data using Finnhub"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"
    
    def get_quote(self, ticker):
        """
        Get real-time quote (FAST - <0.2 seconds)
        
        Returns:
            dict with current price, change, etc.
        """
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': ticker,
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=2)
            data = response.json()
            
            if 'c' in data:  # c = current price
                return {
                    'symbol': ticker,
                    'price': data['c'],
                    'change': data['d'],
                    'change_percent': data['dp'],
                    'high': data['h'],
                    'low': data['l'],
                    'open': data['o'],
                    'prev_close': data['pc'],
                    'timestamp': data['t']
                }
            return None
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None
    
    def get_multiple_quotes(self, tickers):
        """
        Get quotes for multiple stocks (batch)
        
        Args:
            tickers: list of ticker symbols
        
        Returns:
            dict of {ticker: quote_data}
        """
        results = {}
        for ticker in tickers:
            quote = self.get_quote(ticker)
            if quote:
                results[ticker] = quote
            time.sleep(0.1)  # Small delay to avoid rate limit
        return results
    
    def get_technical_indicators(self, ticker):
        """
        Get technical indicators from Finnhub
        
        Returns:
            dict with RSI, SMA, etc.
        """
        try:
            url = f"{self.base_url}/scan/technical-indicator"
            params = {
                'symbol': ticker,
                'resolution': 'D',
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=2)
            data = response.json()
            
            if 'technicalAnalysis' in data:
                return {
                    'symbol': ticker,
                    'signal': data['technicalAnalysis']['signal'],
                    'count': data['technicalAnalysis']['count']
                }
            return None
        except Exception as e:
            return None


# Speed test
def speed_test():
    """Compare speed of different data sources"""
    import yfinance as yf
    
    print("\n" + "=" * 80)
    print("⚡ SPEED TEST - Data Fetching Comparison")
    print("=" * 80)
    
    test_ticker = "AAPL"
    
    # Test Finnhub
    print(f"\n1. Testing Finnhub (Fast)...")
    fetcher = FastDataFetcher()
    start = time.time()
    data = fetcher.get_quote(test_ticker)
    finnhub_time = time.time() - start
    print(f"   ✅ Finnhub: {finnhub_time:.3f} seconds")
    if data:
        print(f"   Price: ${data['price']:.2f} ({data['change_percent']:+.2f}%)")
    
    # Test yfinance
    print(f"\n2. Testing yfinance (Slow)...")
    start = time.time()
    stock = yf.Ticker(test_ticker)
    hist = stock.history(period="5d")
    yfinance_time = time.time() - start
    print(f"   ✅ yfinance: {yfinance_time:.3f} seconds")
    if not hist.empty:
        print(f"   Price: ${hist['Close'].iloc[-1]:.2f}")
    
    # Test Binance (for comparison)
    print(f"\n3. Testing Binance (Crypto - Fast)...")
    start = time.time()
    response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
    binance_time = time.time() - start
    print(f"   ✅ Binance: {binance_time:.3f} seconds")
    print(f"   BTC Price: ${float(response.json()['price']):,.2f}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SPEED COMPARISON:")
    print(f"   Finnhub:  {finnhub_time:.3f}s  {'⚡' * int(5 - finnhub_time)}")
    print(f"   yfinance: {yfinance_time:.3f}s  {'🐌' * int(yfinance_time / 2)}")
    print(f"   Binance:  {binance_time:.3f}s  {'⚡' * 5}")
    print("=" * 80)
    
    speedup = yfinance_time / finnhub_time
    print(f"\n🚀 Finnhub is {speedup:.1f}x FASTER than yfinance!")
    print("=" * 80)


if __name__ == "__main__":
    speed_test()
