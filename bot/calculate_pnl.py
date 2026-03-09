#!/usr/bin/env python3
"""
Calculate Profit/Loss from Bot Trading Activity
Analyzes all filled orders and calculates realized P&L
"""

import requests
from datetime import datetime
from collections import defaultdict

# IBKR Gateway API endpoint
BASE_URL = "https://localhost:5055/v1/api"

def get_all_orders():
    """Fetch all orders from IBKR"""
    try:
        response = requests.get(
            f"{BASE_URL}/iserver/account/orders",
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('orders', [])
        else:
            print(f"❌ Error fetching orders: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def calculate_pnl(orders):
    """Calculate P&L from filled orders"""
    
    # Group orders by symbol
    trades_by_symbol = defaultdict(list)
    
    for order in orders:
        if order.get('status') != 'Filled':
            continue
            
        symbol = order.get('ticker', 'UNKNOWN')
        side = order.get('side', '')
        filled_qty = float(order.get('filledQuantity', 0))
        avg_price = float(order.get('avgPrice', 0))
        
        if filled_qty == 0 or avg_price == 0:
            continue
        
        trades_by_symbol[symbol].append({
            'side': side,
            'quantity': filled_qty,
            'price': avg_price,
            'value': filled_qty * avg_price,
            'order_id': order.get('orderId'),
            'time': order.get('lastExecutionTime', '')
        })
    
    return trades_by_symbol

def analyze_trades(trades_by_symbol):
    """Analyze trades and calculate P&L"""
    
    total_pnl = 0
    total_buys = 0
    total_sells = 0
    
    print("\n" + "="*100)
    print("BOT TRADING PROFIT/LOSS ANALYSIS")
    print("="*100)
    
    for symbol, trades in sorted(trades_by_symbol.items()):
        print(f"\n📊 {symbol}")
        print("-" * 100)
        
        buys = [t for t in trades if t['side'] == 'BUY']
        sells = [t for t in trades if t['side'] == 'SELL']
        
        total_buy_qty = sum(t['quantity'] for t in buys)
        total_sell_qty = sum(t['quantity'] for t in sells)
        
        total_buy_value = sum(t['value'] for t in buys)
        total_sell_value = sum(t['value'] for t in sells)
        
        avg_buy_price = total_buy_value / total_buy_qty if total_buy_qty > 0 else 0
        avg_sell_price = total_sell_value / total_sell_qty if total_sell_qty > 0 else 0
        
        # Calculate realized P&L (only on closed positions)
        closed_qty = min(total_buy_qty, total_sell_qty)
        realized_pnl = 0
        
        if closed_qty > 0:
            realized_pnl = (avg_sell_price - avg_buy_price) * closed_qty
        
        # Display trade details
        print(f"   BUY:  {total_buy_qty:>8.2f} shares @ ${avg_buy_price:>8.2f} avg = ${total_buy_value:>12,.2f}")
        print(f"   SELL: {total_sell_qty:>8.2f} shares @ ${avg_sell_price:>8.2f} avg = ${total_sell_value:>12,.2f}")
        print(f"   ")
        print(f"   Closed Position: {closed_qty:.2f} shares")
        
        if realized_pnl > 0:
            print(f"   💰 Realized P&L: ${realized_pnl:>12,.2f} ✅ PROFIT")
        elif realized_pnl < 0:
            print(f"   💸 Realized P&L: ${realized_pnl:>12,.2f} ❌ LOSS")
        else:
            print(f"   ⚪ Realized P&L: ${realized_pnl:>12,.2f} (No closed positions)")
        
        # Open position
        open_qty = total_buy_qty - total_sell_qty
        if open_qty != 0:
            open_value = open_qty * avg_buy_price
            print(f"   📈 Open Position: {open_qty:+.2f} shares (${open_value:,.2f} cost basis)")
        
        total_pnl += realized_pnl
        total_buys += total_buy_value
        total_sells += total_sell_value
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    print(f"Total Buy Value:  ${total_buys:>15,.2f}")
    print(f"Total Sell Value: ${total_sells:>15,.2f}")
    print(f"")
    
    if total_pnl > 0:
        print(f"💰 TOTAL REALIZED P&L: ${total_pnl:>15,.2f} ✅ PROFIT")
        roi = (total_pnl / total_buys * 100) if total_buys > 0 else 0
        print(f"📊 Return on Investment: {roi:>14.2f}%")
    elif total_pnl < 0:
        print(f"💸 TOTAL REALIZED P&L: ${total_pnl:>15,.2f} ❌ LOSS")
        roi = (total_pnl / total_buys * 100) if total_buys > 0 else 0
        print(f"📊 Return on Investment: {roi:>14.2f}%")
    else:
        print(f"⚪ TOTAL REALIZED P&L: ${total_pnl:>15,.2f} (No closed positions yet)")
    
    print("="*100)
    print("\n")

def main():
    print("🔍 Fetching all orders from IBKR...")
    
    orders = get_all_orders()
    
    if not orders:
        print("❌ No orders found or unable to fetch orders")
        return
    
    print(f"✅ Found {len(orders)} total orders")
    
    # Filter only filled orders
    filled_orders = [o for o in orders if o.get('status') == 'Filled']
    print(f"✅ {len(filled_orders)} filled orders")
    
    if not filled_orders:
        print("❌ No filled orders to analyze")
        return
    
    # Calculate P&L
    trades_by_symbol = calculate_pnl(filled_orders)
    
    # Analyze and display
    analyze_trades(trades_by_symbol)

if __name__ == "__main__":
    main()
