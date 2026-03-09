#!/usr/bin/env python3
"""
Crypto Trading Bot for Binance
Monitors and analyzes crypto prices with trading signals
"""

import requests
import time
from datetime import datetime


class CryptoBot:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.symbol = "BTCUSDT"
        self.price_history = []
        
    def get_current_price(self, symbol=None):
        """Get current price for a symbol"""
        symbol = symbol or self.symbol
        try:
            url = f"{self.base_url}/ticker/price?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            return float(data['price'])
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    
    def get_24h_stats(self, symbol=None):
        """Get 24h statistics"""
        symbol = symbol or self.symbol
        try:
            url = f"{self.base_url}/ticker/24hr?symbol={symbol}"
            response = requests.get(url)
            data = response.json()
            return {
                'symbol': symbol,
                'price': float(data['lastPrice']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'volume_24h': float(data['volume']),
                'price_change': float(data['priceChange']),
                'price_change_percent': float(data['priceChangePercent']),
                'trades': int(data['count'])
            }
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return None
    
    def get_klines(self, symbol=None, interval='1h', limit=24):
        """
        Get candlestick data
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            interval: 1m, 5m, 15m, 1h, 4h, 1d, etc.
            limit: Number of candles to fetch
        """
        symbol = symbol or self.symbol
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            candles = []
            for candle in data:
                candles.append({
                    'timestamp': candle[0],
                    'open': float(candle[1]),
                    'high': float(candle[2]),
                    'low': float(candle[3]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                })
            return candles
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return []
    
    def calculate_sma(self, prices, period):
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
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
    
    def analyze_market(self):
        """Analyze market and generate trading signals"""
        stats = self.get_24h_stats()
        if not stats:
            return None
        
        # Get hourly candles for last 24 hours
        candles = self.get_klines(interval='1h', limit=24)
        if not candles:
            return None
        
        prices = [c['close'] for c in candles]
        
        # Calculate indicators
        sma_12 = self.calculate_sma(prices, 12)
        sma_24 = self.calculate_sma(prices, 24)
        rsi = self.calculate_rsi(prices)
        
        current_price = stats['price']
        
        # Generate signal
        signal = "HOLD"
        reason = []
        
        # RSI signals
        if rsi and rsi < 30:
            signal = "BUY"
            reason.append(f"RSI oversold ({rsi:.1f})")
        elif rsi and rsi > 70:
            signal = "SELL"
            reason.append(f"RSI overbought ({rsi:.1f})")
        
        # Moving average crossover
        if sma_12 and sma_24:
            if sma_12 > sma_24 and current_price > sma_12:
                if signal != "SELL":
                    signal = "BUY"
                reason.append("Price above SMAs (bullish)")
            elif sma_12 < sma_24 and current_price < sma_12:
                if signal != "BUY":
                    signal = "SELL"
                reason.append("Price below SMAs (bearish)")
        
        # 24h momentum
        if stats['price_change_percent'] > 5:
            reason.append("Strong upward momentum")
        elif stats['price_change_percent'] < -5:
            reason.append("Strong downward momentum")
        
        return {
            'signal': signal,
            'reason': reason,
            'price': current_price,
            'rsi': rsi,
            'sma_12': sma_12,
            'sma_24': sma_24,
            'change_24h': stats['price_change_percent']
        }
    
    def display_analysis(self):
        """Display market analysis"""
        print("\n" + "=" * 70)
        print(f"CRYPTO MARKET ANALYSIS - {self.symbol}")
        print("=" * 70)
        
        stats = self.get_24h_stats()
        if not stats:
            print("Failed to fetch market data")
            return
        
        print(f"\n📊 Current Price: ${stats['price']:,.2f}")
        print(f"📈 24h High: ${stats['high_24h']:,.2f}")
        print(f"📉 24h Low: ${stats['low_24h']:,.2f}")
        print(f"💹 24h Change: {stats['price_change_percent']:+.2f}%")
        print(f"📦 24h Volume: {stats['volume_24h']:,.2f} BTC")
        print(f"🔄 24h Trades: {stats['trades']:,}")
        
        analysis = self.analyze_market()
        if analysis:
            print(f"\n🎯 SIGNAL: {analysis['signal']}")
            print(f"📊 RSI: {analysis['rsi']:.1f}" if analysis['rsi'] else "📊 RSI: N/A")
            print(f"📈 SMA(12h): ${analysis['sma_12']:,.2f}" if analysis['sma_12'] else "")
            print(f"📈 SMA(24h): ${analysis['sma_24']:,.2f}" if analysis['sma_24'] else "")
            
            if analysis['reason']:
                print(f"\n💡 Reasons:")
                for r in analysis['reason']:
                    print(f"   • {r}")
        
        print("=" * 70)
    
    def monitor(self, interval=60):
        """Monitor crypto market continuously"""
        print("\n🤖 Crypto Bot Started - Press Ctrl+C to stop\n")
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n[{timestamp}]")
                
                self.display_analysis()
                
                print(f"\nNext update in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")


def main():
    bot = CryptoBot()
    
    print("\n" + "=" * 70)
    print("CRYPTO TRADING BOT")
    print("=" * 70)
    print("\nThis bot monitors BTC/USDT and provides trading signals based on:")
    print("  • RSI (Relative Strength Index)")
    print("  • Moving Averages (SMA 12h & 24h)")
    print("  • 24h Price Momentum")
    print("\nSignals: BUY, SELL, or HOLD")
    print("=" * 70)
    
    # Show initial analysis
    bot.display_analysis()
    
    print("\n")
    choice = input("Start continuous monitoring? (y/n): ").lower()
    
    if choice == 'y':
        bot.monitor(interval=60)  # Update every 60 seconds
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
