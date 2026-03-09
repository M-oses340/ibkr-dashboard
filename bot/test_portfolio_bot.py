#!/usr/bin/env python3
"""Test the portfolio bot in analysis mode"""

import sys
sys.path.insert(0, '/home/charles/StudioProjects/ibk/interactive-brokers-web-api/bot')

from portfolio_bot import PortfolioBot

print("\n" + "=" * 80)
print("🧪 PORTFOLIO BOT - ANALYSIS MODE")
print("=" * 80)

bot = PortfolioBot()
portfolio = bot.get_portfolio()

print(f"\n📊 Analyzing {len(portfolio)} positions:\n")

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
print("✅ Analysis complete!")
