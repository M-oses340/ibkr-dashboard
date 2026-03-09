#!/usr/bin/env python3
"""
Polymarket Data Demo - Shows what data you can fetch
"""

import requests
import json

print("\n" + "=" * 80)
print("🎯 POLYMARKET DATA - What You Can Fetch")
print("=" * 80)

# Fetch active markets
try:
    url = "https://gamma-api.polymarket.com/markets"
    params = {'limit': 5, 'active': True}
    response = requests.get(url, params=params, timeout=10)
    markets = response.json()
    
    print("\n📊 SAMPLE PREDICTION MARKETS:\n")
    
    for i, market in enumerate(markets, 1):
        print(f"{i}. {market.get('question', 'N/A')}")
        print(f"   Description: {market.get('description', 'N/A')[:100]}...")
        print(f"   Category: {market.get('category', 'N/A')}")
        print(f"   End Date: {market.get('end_date_iso', 'N/A')}")
        
        # Show outcomes and probabilities
        outcomes = market.get('outcomes', [])
        if outcomes:
            print(f"   Outcomes:")
            for outcome in outcomes:
                outcome_text = outcome.get('outcome', 'N/A')
                price = outcome.get('price', 0)
                try:
                    prob = float(price) * 100
                    print(f"      • {outcome_text}: {prob:.1f}% probability")
                except:
                    print(f"      • {outcome_text}: {price}")
        
        print()
    
    print("=" * 80)
    print("\n📋 TYPES OF DATA AVAILABLE:\n")
    print("1. ✅ Event Probabilities (0-100%)")
    print("   - Fed rate decisions")
    print("   - Election outcomes")
    print("   - Economic indicators")
    print("   - Company earnings")
    print("   - Crypto price targets")
    
    print("\n2. ✅ Market Metadata")
    print("   - Trading volume")
    print("   - Liquidity")
    print("   - Number of traders")
    print("   - End dates")
    
    print("\n3. ✅ Categories")
    print("   - Politics")
    print("   - Crypto")
    print("   - Business")
    print("   - Sports")
    print("   - Science")
    
    print("\n4. ✅ Real-time Updates")
    print("   - Probabilities change as people trade")
    print("   - Reflects latest information")
    print("   - Crowd-sourced predictions")
    
    print("\n" + "=" * 80)
    print("\n💡 HOW TO USE FOR TRADING:\n")
    print("Example 1: Fed Rate Decision")
    print("   Polymarket: 'Will Fed cut rates?' → 80% YES")
    print("   Your Action: BUY rate-sensitive stocks (JPM, BAC)")
    
    print("\nExample 2: Bitcoin Price Target")
    print("   Polymarket: 'BTC above $100k by Dec?' → 60% YES")
    print("   Your Action: Increase BTC position")
    
    print("\nExample 3: Company Earnings")
    print("   Polymarket: 'Will NVDA beat earnings?' → 75% YES")
    print("   Your Action: BUY NVDA before earnings")
    
    print("\nExample 4: Economic Data")
    print("   Polymarket: 'Inflation >3%?' → 70% YES")
    print("   Your Action: BUY inflation hedges (gold, commodities)")
    
    print("\n" + "=" * 80)
    
except Exception as e:
    print(f"\n❌ Error fetching Polymarket data: {e}")
    print("\nPolymarket provides:")
    print("- Event probabilities (crowd-sourced predictions)")
    print("- Market sentiment on future events")
    print("- Trading signals based on real-world outcomes")
    print("\nUseful for: Predicting market-moving events before they happen")
