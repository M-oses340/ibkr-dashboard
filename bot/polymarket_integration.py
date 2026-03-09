#!/usr/bin/env python3
"""
Polymarket Integration for Trading Decisions
Uses prediction market probabilities to inform trading strategies
"""

import requests
import json
from datetime import datetime

class PolymarketAnalyzer:
    """Fetch and analyze Polymarket prediction data"""
    
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self.gamma_url = "https://gamma-api.polymarket.com"
    
    def search_markets(self, query):
        """
        Search for prediction markets
        
        Args:
            query: Search term (e.g., "Fed", "Bitcoin", "NVDA")
        
        Returns:
            list of relevant markets
        """
        try:
            url = f"{self.gamma_url}/markets"
            params = {
                'limit': 10,
                'offset': 0
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            # Filter by query
            markets = []
            for market in data:
                if query.lower() in market.get('question', '').lower():
                    markets.append({
                        'question': market.get('question'),
                        'description': market.get('description'),
                        'end_date': market.get('end_date_iso'),
                        'volume': market.get('volume'),
                        'liquidity': market.get('liquidity'),
                        'outcomes': market.get('outcomes', [])
                    })
            
            return markets
        except Exception as e:
            print(f"Error searching markets: {e}")
            return []
    
    def get_market_probability(self, market_id):
        """
        Get current probability for a market
        
        Returns:
            float: probability (0-1)
        """
        try:
            url = f"{self.gamma_url}/markets/{market_id}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            # Get YES outcome probability
            for outcome in data.get('outcomes', []):
                if outcome.get('outcome') == 'Yes':
                    return float(outcome.get('price', 0))
            
            return None
        except Exception as e:
            return None
    
    def get_fed_rate_probability(self):
        """Get probability of Fed rate cut"""
        markets = self.search_markets("Federal Reserve rate")
        if markets:
            return {
                'question': markets[0]['question'],
                'probability': markets[0]['outcomes'][0].get('price', 0) if markets[0]['outcomes'] else 0,
                'volume': markets[0]['volume']
            }
        return None
    
    def get_bitcoin_predictions(self):
        """Get Bitcoin price predictions"""
        markets = self.search_markets("Bitcoin")
        predictions = []
        
        for market in markets[:3]:
            predictions.append({
                'question': market['question'],
                'end_date': market['end_date'],
                'volume': market['volume']
            })
        
        return predictions
    
    def get_stock_earnings_prediction(self, ticker):
        """Get earnings beat probability for a stock"""
        markets = self.search_markets(f"{ticker} earnings")
        if markets:
            return {
                'question': markets[0]['question'],
                'probability': markets[0]['outcomes'][0].get('price', 0) if markets[0]['outcomes'] else 0
            }
        return None
    
    def generate_trading_signals(self):
        """
        Generate trading signals based on Polymarket probabilities
        
        Returns:
            dict with trading recommendations
        """
        signals = {
            'timestamp': datetime.now().isoformat(),
            'recommendations': []
        }
        
        # Check Fed rate decision
        fed_data = self.get_fed_rate_probability()
        if fed_data and fed_data['probability'] > 0.7:
            signals['recommendations'].append({
                'event': 'Fed Rate Cut Likely',
                'probability': fed_data['probability'],
                'action': 'BUY rate-sensitive stocks (banks, real estate)',
                'tickers': ['JPM', 'BAC', 'VNQ']
            })
        
        # Check Bitcoin predictions
        btc_predictions = self.get_bitcoin_predictions()
        if btc_predictions:
            signals['recommendations'].append({
                'event': 'Bitcoin Predictions',
                'markets': btc_predictions,
                'action': 'Monitor BTC position'
            })
        
        return signals


# Example usage and demo
def demo():
    """Demo Polymarket integration"""
    print("\n" + "=" * 80)
    print("🎯 POLYMARKET INTEGRATION - Prediction Markets for Trading")
    print("=" * 80)
    
    analyzer = PolymarketAnalyzer()
    
    # Search for Fed-related markets
    print("\n1. Federal Reserve Predictions:")
    print("-" * 80)
    fed_markets = analyzer.search_markets("Federal Reserve")
    for market in fed_markets[:3]:
        print(f"\n❓ {market['question']}")
        print(f"   End Date: {market['end_date']}")
        print(f"   Volume: ${market['volume']:,.0f}")
        if market['outcomes']:
            for outcome in market['outcomes']:
                prob = outcome.get('price', 0)
                print(f"   {outcome.get('outcome')}: {prob*100:.1f}%")
    
    # Search for Bitcoin markets
    print("\n\n2. Bitcoin Predictions:")
    print("-" * 80)
    btc_markets = analyzer.search_markets("Bitcoin")
    for market in btc_markets[:3]:
        print(f"\n❓ {market['question']}")
        print(f"   Volume: ${market['volume']:,.0f}")
    
    # Search for stock earnings
    print("\n\n3. Stock Earnings Predictions:")
    print("-" * 80)
    for ticker in ['NVDA', 'AAPL', 'TSLA']:
        markets = analyzer.search_markets(f"{ticker}")
        if markets:
            print(f"\n📊 {ticker}:")
            print(f"   {markets[0]['question']}")
    
    # Generate trading signals
    print("\n\n4. Trading Signals Based on Predictions:")
    print("-" * 80)
    signals = analyzer.generate_trading_signals()
    for rec in signals['recommendations']:
        print(f"\n🎯 {rec['event']}")
        if 'probability' in rec:
            print(f"   Probability: {rec['probability']*100:.1f}%")
        print(f"   Action: {rec['action']}")
        if 'tickers' in rec:
            print(f"   Suggested: {', '.join(rec['tickers'])}")
    
    print("\n" + "=" * 80)
    print("\n💡 How to use this:")
    print("   1. Monitor high-probability events (>70%)")
    print("   2. Trade before events happen")
    print("   3. Adjust positions based on changing probabilities")
    print("   4. Combine with technical analysis for best results")
    print("=" * 80)


if __name__ == "__main__":
    demo()
