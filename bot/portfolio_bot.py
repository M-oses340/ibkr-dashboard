#!/usr/bin/env python3
"""
Multi-Asset Portfolio Trading Bot
Monitors and trades all positions in your IBKR portfolio
Enhanced with yfinance for advanced technical analysis
"""

import requests
import time
import os
from datetime import datetime
import yfinance as yf

# Disable SSL warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Configuration
IBKR_API_URL = "https://localhost:5055/v1/api"
ACCOUNT_ID = os.environ.get('IBKR_ACCOUNT_ID', 'DUP158699')
BINANCE_API = "https://api.binance.com/api/v3"
FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY', 'd6nd9t9r01qodk5v9t30d6nd9t9r01qodk5v9t3g')  # Your API key

# Trading settings
TRADE_PERCENT = 0.05  # Trade 5% of position size
MIN_TRADE_VALUE = 100  # Minimum $100 per trade
CHECK_INTERVAL = 30  # Check every 30 seconds


class PortfolioBot:
    def __init__(self):
        self.positions = {}
        self.last_signals = {}
        self.tech_data_cache = {}  # Cache technical data
        self.cache_timestamp = {}  # Track when data was cached
        self.cache_duration = 60  # Cache for 60 seconds
        self.finnhub_url = "https://finnhub.io/api/v1"
        self.use_finnhub = True  # Set to False to use yfinance instead
        
    def get_portfolio(self):
        """Fetch current portfolio from IBKR"""
        try:
            url = f"{IBKR_API_URL}/portfolio/{ACCOUNT_ID}/positions/0"
            response = requests.get(url, verify=False)
            
            if response.content:
                positions = response.json()
                portfolio = {}
                
                for pos in positions:
                    conid = pos.get('conid')
                    ticker = pos.get('ticker', 'N/A')
                    position = float(pos.get('position', 0))
                    asset_class = pos.get('assetClass', 'STK')
                    mkt_value = float(pos.get('mktValue', 0))
                    mkt_price = float(pos.get('mktPrice', 0))
                    
                    # Skip futures and very small positions
                    if asset_class == 'FUT' or abs(mkt_value) < 100:
                        continue
                    
                    portfolio[conid] = {
                        'ticker': ticker,
                        'position': position,
                        'asset_class': asset_class,
                        'mkt_value': mkt_value,
                        'mkt_price': mkt_price
                    }
                
                return portfolio
            return {}
        except Exception as e:
            print(f"❌ Error fetching portfolio: {e}")
            return {}
    
    def get_crypto_price(self, ticker):
        """Get crypto price from Binance"""
        try:
            symbol_map = {
                'BTC': 'BTCUSDT',
                'ETH': 'ETHUSDT',
                'LTC': 'LTCUSDT',
                'SOL': 'SOLUSDT'
            }
            
            symbol = symbol_map.get(ticker)
            if not symbol:
                return None
            
            url = f"{BINANCE_API}/ticker/24hr?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            
            return {
                'price': float(data['lastPrice']),
                'change_percent': float(data['priceChangePercent'])
            }
        except Exception as e:
            return None
    
    def get_stock_data_finnhub(self, ticker):
        """Get real-time stock data from Finnhub (FAST - 0.2 seconds)"""
        try:
            # Check cache first
            current_time = time.time()
            cache_key = f"finnhub_{ticker}"
            if cache_key in self.tech_data_cache:
                cache_age = current_time - self.cache_timestamp.get(cache_key, 0)
                if cache_age < self.cache_duration:
                    return self.tech_data_cache[cache_key]
            
            # Fetch real-time quote
            url = f"{self.finnhub_url}/quote"
            params = {
                'symbol': ticker,
                'token': FINNHUB_API_KEY
            }
            
            response = requests.get(url, params=params, timeout=2)
            data = response.json()
            
            if 'c' in data and data['c'] > 0:  # c = current price
                result = {
                    'price': data['c'],
                    'change': data['d'],
                    'change_percent': data['dp'],
                    'high': data['h'],
                    'low': data['l'],
                    'open': data['o'],
                    'prev_close': data['pc']
                }
                
                # Cache the result
                self.tech_data_cache[cache_key] = result
                self.cache_timestamp[cache_key] = current_time
                
                return result
            return None
        except Exception as e:
            return None
    
    def get_stock_data(self, conid):
        """Get stock market data from IBKR"""
        try:
            url = f"{IBKR_API_URL}/iserver/marketdata/snapshot?conids={conid}&fields=31,84,86"
            response = requests.get(url, verify=False)
            
            if response.content:
                data = response.json()
                if data and len(data) > 0:
                    snapshot = data[0]
                    
                    # Field 31 = Last Price, 84 = Bid, 86 = Ask
                    # Field 7295 = Previous Close (if available)
                    last_price = snapshot.get('31')
                    
                    if last_price:
                        return {'last_price': float(last_price)}
            return None
        except Exception as e:
            return None
    
    def get_stock_technical_data(self, ticker):
        """Get stock technical analysis data using yfinance with caching"""
        try:
            # Check cache first
            current_time = time.time()
            if ticker in self.tech_data_cache:
                cache_age = current_time - self.cache_timestamp.get(ticker, 0)
                if cache_age < self.cache_duration:
                    return self.tech_data_cache[ticker]
            
            # Fetch fresh data
            stock = yf.Ticker(ticker)
            
            # Get historical data (last 60 days for indicators)
            hist = stock.history(period="60d")
            
            if hist.empty:
                return None
            
            # Calculate technical indicators
            closes = hist['Close'].values
            
            # RSI (14-period)
            rsi = self.calculate_rsi(closes, 14)
            
            # Moving averages
            sma_20 = closes[-20:].mean() if len(closes) >= 20 else None
            sma_50 = closes[-50:].mean() if len(closes) >= 50 else None
            
            # Current price and change
            current_price = closes[-1]
            prev_close = closes[-2] if len(closes) > 1 else current_price
            change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
            
            # Volume analysis
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            result = {
                'price': current_price,
                'change_percent': change_percent,
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'volume_ratio': volume_ratio,
                'avg_volume': avg_volume
            }
            
            # Cache the result
            self.tech_data_cache[ticker] = result
            self.cache_timestamp[ticker] = current_time
            
            return result
        except Exception as e:
            print(f"   ⚠️  Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def analyze_asset(self, ticker, asset_class, position, mkt_value, conid=None):
        """Analyze asset and generate trading signal with fast Finnhub data"""
        
        # For crypto, use Binance data
        if asset_class == 'CRYPTO':
            crypto_data = self.get_crypto_price(ticker)
            if not crypto_data:
                return 'HOLD', []
            
            change = crypto_data['change_percent']
            reasons = []
            
            # Simple momentum strategy
            if change > 2:
                reasons.append(f"Strong upward momentum ({change:+.2f}%)")
                return 'BUY', reasons
            elif change < -2:
                reasons.append(f"Strong downward momentum ({change:+.2f}%)")
                return 'SELL', reasons
            else:
                return 'HOLD', []
        
        # For stocks, use Finnhub for fast real-time data
        else:
            reasons = []
            
            # Try Finnhub first (fast)
            if self.use_finnhub:
                finnhub_data = self.get_stock_data_finnhub(ticker)
                if finnhub_data:
                    change_percent = finnhub_data['change_percent']
                    price = finnhub_data['price']
                    
                    # Quick momentum signals
                    if change_percent > 5:
                        reasons.append(f"Strong rally ({change_percent:+.2f}%)")
                        if position > 0:
                            return 'BUY', reasons
                    elif change_percent < -5:
                        reasons.append(f"Sharp decline ({change_percent:+.2f}%)")
                        if position > 0:
                            return 'SELL', reasons
            
            # Get detailed technical data from yfinance (cached for 60 seconds)
            tech_data = self.get_stock_technical_data(ticker)
            
            if tech_data:
                rsi = tech_data.get('rsi')
                sma_20 = tech_data.get('sma_20')
                sma_50 = tech_data.get('sma_50')
                price = tech_data.get('price')
                change_percent = tech_data.get('change_percent')
                volume_ratio = tech_data.get('volume_ratio')
                
                # RSI-based signals
                if rsi:
                    if rsi < 30:
                        reasons.append(f"RSI oversold ({rsi:.1f})")
                        return 'BUY', reasons
                    elif rsi > 70:
                        reasons.append(f"RSI overbought ({rsi:.1f})")
                        if position > 0:
                            return 'SELL', reasons
                
                # Moving average crossover
                if sma_20 and sma_50 and price:
                    if price > sma_20 > sma_50:
                        reasons.append(f"Bullish trend (Price > SMA20 > SMA50)")
                        if position > 0 and mkt_value > 10000:
                            return 'BUY', reasons
                    elif price < sma_20 < sma_50:
                        reasons.append(f"Bearish trend (Price < SMA20 < SMA50)")
                        if position > 0:
                            return 'SELL', reasons
                
                # Volume spike with price movement
                if volume_ratio and volume_ratio > 2:
                    if change_percent > 3:
                        reasons.append(f"High volume breakout ({volume_ratio:.1f}x avg volume, +{change_percent:.1f}%)")
                        return 'BUY', reasons
                    elif change_percent < -3:
                        reasons.append(f"High volume breakdown ({volume_ratio:.1f}x avg volume, {change_percent:.1f}%)")
                        if position > 0:
                            return 'SELL', reasons
            
            # Fallback to position-based strategy
            if position > 0:
                if ticker in ['NVDA', 'AAPL', 'TSLA', 'MSTR', 'UBER', 'NIO']:
                    if mkt_value > 10000:
                        reasons.append(f"Large tech position (${mkt_value:,.0f})")
                        return 'BUY', reasons
                
                elif ticker in ['SCHD', 'SGOV', 'VTEB', 'MUNY']:
                    return 'HOLD', []
                
                elif ticker in ['SQQQ', 'SOXS']:
                    if mkt_value > 50000:
                        reasons.append(f"Large leveraged position - take profits")
                        return 'SELL', reasons
            
            elif position < 0:
                if abs(mkt_value) > 15000:
                    reasons.append(f"Large short position (${abs(mkt_value):,.0f}) - reduce risk")
                    return 'BUY', reasons
            
            return 'HOLD', []
    
    def place_order(self, conid, side, quantity, asset_class, ticker):
        """Place order on IBKR"""
        try:
            # For crypto, use cashQty
            if asset_class == 'CRYPTO':
                data = {
                    "orders": [{
                        "conid": conid,
                        "orderType": "MKT",
                        "cashQty": round(quantity, 2),
                        "side": side,
                        "tif": "IOC"
                    }]
                }
            else:
                # For stocks, use regular quantity
                data = {
                    "orders": [{
                        "conid": conid,
                        "orderType": "MKT",
                        "quantity": int(abs(quantity)),
                        "side": side,
                        "tif": "DAY"
                    }]
                }
            
            url = f"{IBKR_API_URL}/iserver/account/{ACCOUNT_ID}/orders"
            response = requests.post(url, json=data, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Order placed: {side} {ticker}")
                print(f"      Response: {result}")
                return True
            else:
                print(f"   ❌ Order failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error placing order: {e}")
            return False
    
    def execute_trade(self, conid, ticker, signal, position, mkt_value, mkt_price, asset_class):
        """Execute trade based on signal"""
        
        # Calculate trade size (5% of position or min $100)
        trade_value = max(abs(mkt_value) * TRADE_PERCENT, MIN_TRADE_VALUE)
        
        if asset_class == 'CRYPTO':
            # For crypto, trade in cash amount
            if signal == 'BUY':
                print(f"   🟢 BUY ${trade_value:.2f} worth of {ticker}")
                return self.place_order(conid, 'BUY', trade_value, asset_class, ticker)
            elif signal == 'SELL' and position > 0:
                sell_value = min(trade_value, abs(mkt_value))
                print(f"   🔴 SELL ${sell_value:.2f} worth of {ticker}")
                return self.place_order(conid, 'SELL', sell_value, asset_class, ticker)
        else:
            # For stocks, trade in shares
            if mkt_price > 0:
                trade_shares = int(trade_value / mkt_price)
                
                if signal == 'BUY':
                    print(f"   🟢 BUY {trade_shares} shares of {ticker}")
                    return self.place_order(conid, 'BUY', trade_shares, asset_class, ticker)
                elif signal == 'SELL' and position > 0:
                    sell_shares = min(trade_shares, int(abs(position)))
                    print(f"   🔴 SELL {sell_shares} shares of {ticker}")
                    return self.place_order(conid, 'SELL', sell_shares, asset_class, ticker)
        
        return False
    
    def run(self):
        """Run the bot continuously"""
        print("\n" + "=" * 80)
        print("🤖 MULTI-ASSET PORTFOLIO TRADING BOT")
        print("=" * 80)
        print(f"Account: {ACCOUNT_ID}")
        print(f"Check interval: {CHECK_INTERVAL} seconds")
        print(f"Trade size: {TRADE_PERCENT*100}% of position (min ${MIN_TRADE_VALUE})")
        print("=" * 80)
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n\n[{timestamp}]")
                print("-" * 80)
                
                # Get current portfolio
                portfolio = self.get_portfolio()
                
                if not portfolio:
                    print("❌ No portfolio data available")
                    time.sleep(CHECK_INTERVAL)
                    continue
                
                print(f"\n📊 Monitoring {len(portfolio)} positions:")
                print()
                
                # Analyze each position
                for conid, data in portfolio.items():
                    ticker = data['ticker']
                    position = data['position']
                    asset_class = data['asset_class']
                    mkt_value = data['mkt_value']
                    mkt_price = data['mkt_price']
                    
                    print(f"📈 {ticker:8} | Pos: {position:10.4f} | Value: ${mkt_value:>12,.2f} | Type: {asset_class}")
                    
                    # Analyze and get signal
                    signal, reasons = self.analyze_asset(ticker, asset_class, position, mkt_value, conid)
                    
                    if reasons:
                        for reason in reasons:
                            print(f"   💡 {reason}")
                    
                    print(f"   🎯 Signal: {signal}")
                    
                    # Execute trade if signal changed
                    last_signal = self.last_signals.get(conid)
                    if signal != last_signal and signal != 'HOLD':
                        print(f"   🔔 Signal changed from {last_signal} to {signal}")
                        self.execute_trade(conid, ticker, signal, position, mkt_value, mkt_price, asset_class)
                        self.last_signals[conid] = signal
                    
                    print()
                
                print(f"⏰ Next check in {CHECK_INTERVAL} seconds...")
                print("-" * 80)
                
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")


def main():
    print("\n⚠️  WARNING: This bot will place REAL orders on your IBKR account!")
    print("⚠️  It will monitor and trade ALL positions in your portfolio")
    print("⚠️  Make sure IBKR Gateway is running and you're logged in")
    print("\nPress Ctrl+C at any time to stop the bot\n")
    
    choice = input("Start portfolio trading bot? (yes/no): ").lower()
    
    if choice == 'yes':
        bot = PortfolioBot()
        bot.run()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()



# Alternative: Run bot in test mode (no actual trades)
def test_mode():
    """Run bot in test mode - analyze only, no trades"""
    print("\n" + "=" * 80)
    print("🧪 PORTFOLIO BOT - TEST MODE (No actual trades)")
    print("=" * 80)
    
    bot = PortfolioBot()
    portfolio = bot.get_portfolio()
    
    print(f"\n📊 Your Portfolio ({len(portfolio)} positions):\n")
    
    for conid, data in portfolio.items():
        ticker = data['ticker']
        position = data['position']
        asset_class = data['asset_class']
        mkt_value = data['mkt_value']
        
        print(f"📈 {ticker:8} | Pos: {position:10.4f} | Value: ${mkt_value:>12,.2f} | Type: {asset_class}")
        
        signal, reasons = bot.analyze_asset(ticker, asset_class, position, mkt_value)
        
        if reasons:
            for reason in reasons:
                print(f"   💡 {reason}")
        
        print(f"   🎯 Signal: {signal}")
        print()
    
    print("=" * 80)
    print("Test mode complete. Run with 'yes' to enable live trading.")
