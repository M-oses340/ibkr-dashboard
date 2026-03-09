#!/usr/bin/env python3
"""
Automated Trading Bot
Fetches crypto data from Binance, analyzes it, and places orders on IBKR
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
BINANCE_API = "https://api.binance.com/api/v3"

# Trading settings
BTC_CONID = 479624278  # BTC/USD on PAXOS
TRADE_QUANTITY = 0.001  # Trade 0.001 BTC (about $67)


class AutoTradingBot:
    def __init__(self):
        self.last_signal = None
        self.position = None
        
    def get_btc_data(self):
        """Fetch BTC data from Binance"""
        try:
            # Get current price and 24h stats
            url = f"{BINANCE_API}/ticker/24hr?symbol=BTCUSDT"
            response = requests.get(url)
            data = response.json()
            
            return {
                'price': float(data['lastPrice']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'change_percent': float(data['priceChangePercent']),
                'volume': float(data['volume'])
            }
        except Exception as e:
            print(f"❌ Error fetching BTC data: {e}")
            return None
    
    def get_klines(self, interval='1h', limit=24):
        """Get candlestick data for analysis"""
        try:
            url = f"{BINANCE_API}/klines"
            params = {
                'symbol': 'BTCUSDT',
                'interval': interval,
                'limit': limit
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            prices = [float(candle[4]) for candle in data]  # Close prices
            return prices
        except Exception as e:
            print(f"❌ Error fetching klines: {e}")
            return []
    
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
    
    def calculate_sma(self, prices, period):
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def analyze_and_decide(self):
        """
        Analyze BTC data and make trading decision
        
        Returns: 'BUY', 'SELL', or 'HOLD'
        """
        btc_data = self.get_btc_data()
        if not btc_data:
            return 'HOLD', "No data available"
        
        prices = self.get_klines(interval='1h', limit=24)
        if not prices:
            return 'HOLD', "No price history"
        
        # Calculate indicators
        rsi = self.calculate_rsi(prices)
        sma_12 = self.calculate_sma(prices, 12)
        current_price = btc_data['price']
        change_24h = btc_data['change_percent']
        
        reasons = []
        signal = 'HOLD'
        
        # Decision logic
        buy_signals = 0
        sell_signals = 0
        
        # RSI signals (very aggressive)
        if rsi:
            if rsi < 50:  # Changed from 40 - buy when RSI is below neutral
                buy_signals += 1
                reasons.append(f"RSI below neutral ({rsi:.1f})")
            elif rsi > 50:  # Changed from 60 - sell when RSI is above neutral
                sell_signals += 1
                reasons.append(f"RSI above neutral ({rsi:.1f})")
        
        # Price momentum (very aggressive)
        if change_24h > 0.1:  # Changed from 1 - any positive movement
            buy_signals += 1
            reasons.append(f"Upward momentum ({change_24h:+.2f}%)")
        elif change_24h < -0.1:  # Changed from -1 - any negative movement
            sell_signals += 1
            reasons.append(f"Downward momentum ({change_24h:+.2f}%)")
        
        # Moving average (very aggressive)
        if sma_12 and current_price > sma_12:  # Changed from 1.005 - any price above SMA
            buy_signals += 1
            reasons.append("Price above SMA (bullish)")
        elif sma_12 and current_price < sma_12:  # Changed from 0.995 - any price below SMA
            sell_signals += 1
            reasons.append("Price below SMA (bearish)")
        
        # Make decision (still only need 1 signal, very aggressive)
        if buy_signals >= 1:
            signal = 'BUY'
        elif sell_signals >= 1:
            signal = 'SELL'
        
        return signal, reasons, btc_data
    
    def get_ibkr_position(self):
        """Check current IBKR position"""
        try:
            url = f"{IBKR_API_URL}/portfolio/{ACCOUNT_ID}/positions/0"
            response = requests.get(url, verify=False)
            
            if response.content:
                positions = response.json()
                for pos in positions:
                    if pos.get('conid') == BTC_CONID:
                        return float(pos.get('position', 0))
            return 0
        except Exception as e:
            print(f"❌ Error checking position: {e}")
            return 0
    
    def place_order(self, side, cash_amount):
        """Place order on IBKR using cash quantity (required for crypto)"""
        try:
            # Round to 2 decimal places (IBKR requirement)
            cash_amount = round(cash_amount, 2)
            
            data = {
                "orders": [{
                    "conid": BTC_CONID,
                    "orderType": "MKT",
                    "cashQty": cash_amount,  # Use cashQty instead of quantity for crypto
                    "side": side,
                    "tif": "IOC"  # Immediate or Cancel (required for crypto)
                }]
            }
            
            url = f"{IBKR_API_URL}/iserver/account/{ACCOUNT_ID}/orders"
            response = requests.post(url, json=data, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Order placed: {side} ${cash_amount}")
                print(f"   Response: {result}")
                return True
            else:
                print(f"❌ Order failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error placing order: {e}")
            return False
    
    def execute_trade(self, signal):
        """Execute trade based on signal - always trades on signals"""
        position = self.get_ibkr_position()
        
        print(f"\n📊 Current Position: {position} BTC")
        
        # Get current BTC price for cash calculation
        btc_data = self.get_btc_data()
        if not btc_data:
            print("❌ Cannot get BTC price, skipping trade")
            return False
        
        btc_price = btc_data['price']
        trade_cash = TRADE_QUANTITY * btc_price  # Convert BTC to USD
        
        if signal == 'BUY':
            print(f"🟢 EXECUTING BUY ORDER - Adding ${trade_cash:.2f} worth of BTC (~{TRADE_QUANTITY} BTC)")
            return self.place_order('BUY', trade_cash)
            
        elif signal == 'SELL' and position > 0:
            # Sell a portion or all
            sell_btc = min(TRADE_QUANTITY, abs(position))
            sell_cash = sell_btc * btc_price
            print(f"🔴 EXECUTING SELL ORDER - Selling ${sell_cash:.2f} worth of BTC (~{sell_btc} BTC)")
            return self.place_order('SELL', sell_cash)
            
        elif signal == 'SELL' and position <= 0:
            print(f"⏸️  No BTC to sell, skipping SELL")
            return False
            
        else:
            print(f"⏸️  Signal is HOLD, no action taken")
            return False
    
    def run(self, interval=60):
        """Run the bot continuously"""
        print("\n" + "=" * 70)
        print("🤖 AUTOMATED TRADING BOT")
        print("=" * 70)
        print(f"Strategy: Analyze BTC data → Trade BTC on IBKR")
        print(f"Check interval: {interval} seconds")
        print(f"Account: {ACCOUNT_ID}")
        print(f"Trade size: {TRADE_QUANTITY} BTC")
        print("=" * 70)
        
        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n\n[{timestamp}]")
                print("-" * 70)
                
                # Analyze market
                signal, reasons, btc_data = self.analyze_and_decide()
                
                if btc_data:
                    print(f"\n📈 BTC Price: ${btc_data['price']:,.2f}")
                    print(f"📊 24h Change: {btc_data['change_percent']:+.2f}%")
                    print(f"📈 24h High: ${btc_data['high_24h']:,.2f}")
                    print(f"📉 24h Low: ${btc_data['low_24h']:,.2f}")
                
                print(f"\n🎯 SIGNAL: {signal}")
                if reasons:
                    print(f"💡 Reasons:")
                    for reason in reasons:
                        print(f"   • {reason}")
                
                # Execute trade if signal changed
                if signal != self.last_signal and signal != 'HOLD':
                    print(f"\n🔔 Signal changed from {self.last_signal} to {signal}")
                    self.execute_trade(signal)
                    self.last_signal = signal
                elif signal == 'HOLD':
                    print(f"\n⏸️  No strong signal, holding current position")
                
                print(f"\n⏰ Next check in {interval} seconds...")
                print("-" * 70)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")


def main():
    print("\n⚠️  WARNING: This bot will place REAL orders on your IBKR account!")
    print("⚠️  Make sure IBKR Gateway is running and you're logged in")
    print("\nPress Ctrl+C at any time to stop the bot\n")
    
    choice = input("Start automated trading? (yes/no): ").lower()
    
    if choice == 'yes':
        bot = AutoTradingBot()
        bot.run(interval=20)  # Check every 20 seconds
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
