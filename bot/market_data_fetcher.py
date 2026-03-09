#!/usr/bin/env python3
"""
Multi-Source Market Data Fetcher
Fetches data from multiple sources for comprehensive analysis
"""

import requests
import json
from datetime import datetime, timedelta

# Disable SSL warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
IBKR_API_URL = "https://localhost:5055/v1/api"
BINANCE_API = "https://api.binance.com/api/v3"
ALPHA_VANTAGE_KEY = "demo"  # Replace with your key from https://www.alphavantage.co/


class MarketDataFetcher:
    """Fetch market data from multiple sources"""
    
    def __init__(self, alpha_vantage_key=None):
        self.av_key = alpha_vantage_key or ALPHA_VANTAGE_KEY
    
    # ==================== CRYPTO DATA (Binance) ====================
    
    def get_crypto_data(self, symbol):
        """
        Get comprehensive crypto data from Binance
        
        Args:
            symbol: Crypto symbol (BTC, ETH, SOL, LTC, etc.)
        
        Returns:
            dict with price, volume, change, and technical data
        """
        try:
            symbol_map = {
                'BTC': 'BTCUSDT',
                'ETH': 'ETHUSDT',
                'LTC': 'LTCUSDT',
                'SOL': 'SOLUSDT',
                'BNB': 'BNBUSDT',
                'ADA': 'ADAUSDT',
                'DOT': 'DOTUSDT',
                'DOGE': 'DOGEUSDT'
            }
            
            binance_symbol = symbol_map.get(symbol, f"{symbol}USDT")
            
            # Get 24h ticker data
            url = f"{BINANCE_API}/ticker/24hr?symbol={binance_symbol}"
            response = requests.get(url)
            data = response.json()
            
            # Get klines for technical analysis
            klines_url = f"{BINANCE_API}/klines"
            params = {
                'symbol': binance_symbol,
                'interval': '1h',
                'limit': 100
            }
            klines_response = requests.get(klines_url, params=params)
            klines = klines_response.json()
            
            # Calculate simple indicators
            closes = [float(k[4]) for k in klines]
            sma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
            sma_50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
            
            return {
                'symbol': symbol,
                'source': 'Binance',
                'price': float(data['lastPrice']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'volume_24h': float(data['volume']),
                'change_24h': float(data['priceChange']),
                'change_percent_24h': float(data['priceChangePercent']),
                'trades_24h': int(data['count']),
                'sma_20': sma_20,
                'sma_50': sma_50,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching crypto data for {symbol}: {e}")
            return None
    
    # ==================== STOCK DATA (Yahoo Finance Alternative) ====================
    
    def get_stock_data_yahoo(self, ticker):
        """
        Get stock data using Yahoo Finance API (free, no key needed)
        
        Args:
            ticker: Stock ticker (AAPL, NVDA, TSLA, etc.)
        
        Returns:
            dict with price, volume, and basic data
        """
        try:
            # Yahoo Finance query API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            params = {
                'interval': '1d',
                'range': '1mo'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                meta = result['meta']
                quote = result['indicators']['quote'][0]
                
                current_price = meta.get('regularMarketPrice')
                prev_close = meta.get('previousClose')
                change = current_price - prev_close if current_price and prev_close else 0
                change_percent = (change / prev_close * 100) if prev_close else 0
                
                return {
                    'symbol': ticker,
                    'source': 'Yahoo Finance',
                    'price': current_price,
                    'prev_close': prev_close,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': meta.get('regularMarketVolume'),
                    'day_high': meta.get('regularMarketDayHigh'),
                    'day_low': meta.get('regularMarketDayLow'),
                    'market_cap': meta.get('marketCap'),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching Yahoo data for {ticker}: {e}")
            return None
    
    # ==================== STOCK DATA (Alpha Vantage) ====================
    
    def get_stock_data_alpha_vantage(self, ticker):
        """
        Get stock data from Alpha Vantage (requires API key)
        
        Args:
            ticker: Stock ticker
        
        Returns:
            dict with comprehensive stock data
        """
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': self.av_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': ticker,
                    'source': 'Alpha Vantage',
                    'price': float(quote.get('05. price', 0)),
                    'volume': int(quote.get('06. volume', 0)),
                    'change': float(quote.get('09. change', 0)),
                    'change_percent': float(quote.get('10. change percent', '0').replace('%', '')),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching Alpha Vantage data for {ticker}: {e}")
            return None
    
    # ==================== IBKR DATA ====================
    
    def get_ibkr_data(self, conid):
        """
        Get market data from IBKR
        
        Args:
            conid: IBKR contract ID
        
        Returns:
            dict with IBKR market data
        """
        try:
            url = f"{IBKR_API_URL}/iserver/marketdata/snapshot"
            params = {
                'conids': conid,
                'fields': '31,84,86,7295,7296'  # Last, Bid, Ask, Close, Volume
            }
            
            response = requests.get(url, params=params, verify=False)
            data = response.json()
            
            if data and len(data) > 0:
                snapshot = data[0]
                return {
                    'conid': conid,
                    'source': 'IBKR',
                    'last_price': snapshot.get('31'),
                    'bid': snapshot.get('84'),
                    'ask': snapshot.get('86'),
                    'prev_close': snapshot.get('7295'),
                    'volume': snapshot.get('7296'),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching IBKR data for {conid}: {e}")
            return None
    
    # ==================== UNIFIED INTERFACE ====================
    
    def get_market_data(self, symbol, asset_type='stock', conid=None):
        """
        Get market data from the best available source
        
        Args:
            symbol: Ticker symbol
            asset_type: 'stock' or 'crypto'
            conid: IBKR contract ID (optional)
        
        Returns:
            dict with market data from best source
        """
        if asset_type == 'crypto':
            return self.get_crypto_data(symbol)
        else:
            # Try Yahoo Finance first (free, no key needed)
            data = self.get_stock_data_yahoo(symbol)
            if data:
                return data
            
            # Fallback to Alpha Vantage
            if self.av_key != "demo":
                data = self.get_stock_data_alpha_vantage(symbol)
                if data:
                    return data
            
            # Fallback to IBKR if conid provided
            if conid:
                return self.get_ibkr_data(conid)
            
            return None


# ==================== EXAMPLE USAGE ====================

def main():
    fetcher = MarketDataFetcher()
    
    print("\n" + "=" * 80)
    print("MARKET DATA FETCHER - DEMO")
    print("=" * 80)
    
    # Test crypto data
    print("\n📊 CRYPTO DATA (Binance):")
    for crypto in ['BTC', 'ETH', 'SOL']:
        data = fetcher.get_crypto_data(crypto)
        if data:
            print(f"\n{crypto}:")
            print(f"  Price: ${data['price']:,.2f}")
            print(f"  24h Change: {data['change_percent_24h']:+.2f}%")
            print(f"  Volume: {data['volume_24h']:,.0f}")
            print(f"  SMA(20): ${data['sma_20']:,.2f}" if data['sma_20'] else "")
    
    # Test stock data
    print("\n\n📈 STOCK DATA (Yahoo Finance):")
    for stock in ['AAPL', 'NVDA', 'TSLA']:
        data = fetcher.get_stock_data_yahoo(stock)
        if data:
            print(f"\n{stock}:")
            print(f"  Price: ${data['price']:,.2f}")
            print(f"  Change: {data['change_percent']:+.2f}%")
            print(f"  Volume: {data['volume']:,}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
