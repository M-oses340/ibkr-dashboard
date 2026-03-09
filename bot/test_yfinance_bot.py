#!/usr/bin/env python3
"""Test the enhanced portfolio bot with yfinance"""

import sys
sys.path.insert(0, '/home/charles/StudioProjects/ibk/interactive-brokers-web-api/bot')

from portfolio_bot import PortfolioBot

print("\n" + "=" * 80)
print("🧪 ENHANCED PORTFOLIO BOT - YFINANCE INTEGRATION TEST")
print("=" * 80)

bot = PortfolioBot()
portfolio = bot.get_portfolio()

print(f"\n📊 Analyzing {len(portfolio)} positions with technical indicators:\n")

# Test on a few key stocks
test_stocks = ['NVDA', 'AAPL', 'TSLA', 'MSTR']

for conid, data in portfolio.items():
    ticker = data['ticker']
    
    if ticker not in test_stocks:
        continue
    
    position = data['position']
    asset_class = data['asset_class']
    mkt_value = data['mkt_value']
    
    print(f"📈 {ticker:8} | Pos: {position:10.4f} | Value: ${mkt_value:>12,.2f}")
    
    # Get technical data
    if asset_class == 'STK':
        tech_data = bot.get_stock_technical_data(ticker)
        if tech_data:
            print(f"   💹 Price: ${tech_data['price']:.2f} ({tech_data['change_percent']:+.2f}%)")
            print(f"   📊 RSI: {tech_data['rsi']:.1f}")
            print(f"   📈 SMA(20): ${tech_data['sma_20']:.2f}")
            print(f"   📈 SMA(50): ${tech_data['sma_50']:.2f}")
            print(f"   📦 Volume: {tech_data['volume_ratio']:.1f}x average")
    
    signal, reasons = bot.analyze_asset(ticker, asset_class, position, mkt_value, conid)
    
    if reasons:
        for reason in reasons:
            print(f"   💡 {reason}")
    
    print(f"   🎯 Signal: {signal}")
    print()

print("=" * 80)
print("✅ yfinance integration working!")
