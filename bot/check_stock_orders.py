#!/usr/bin/env python3
import requests
import json

requests.packages.urllib3.disable_warnings()

response = requests.get("https://localhost:5055/v1/api/iserver/account/orders", verify=False)
data = response.json()

print("\n" + "=" * 100)
print("STOCK ORDERS PLACED BY BOT")
print("=" * 100)

# Filter for stock orders only (exclude crypto)
stock_orders = [o for o in data.get('orders', []) if o.get('secType') == 'STK']

# Get recent bot orders (order IDs > 659433000)
bot_orders = [o for o in stock_orders if o.get('orderId', 0) >= 659433000]

if bot_orders:
    print(f"\nFound {len(bot_orders)} stock orders from the bot:\n")
    
    for order in bot_orders:
        order_id = order.get('orderId', 'N/A')
        ticker = order.get('ticker', 'N/A')
        desc = order.get('orderDesc', 'N/A')
        status = order.get('status', 'N/A')
        side = order.get('side', 'N/A')
        qty = order.get('totalSize', 0)
        filled_qty = order.get('filledQuantity', 0)
        avg_price = order.get('avgPrice', 'N/A')
        
        status_icon = "✅" if status == "Filled" else "⏳" if status in ["PreSubmitted", "Submitted"] else "❌"
        
        print(f"{status_icon} Order ID: {order_id}")
        print(f"   Stock: {ticker}")
        print(f"   Action: {side} {qty} shares")
        print(f"   Status: {status}")
        if status == "Filled":
            print(f"   Filled: {filled_qty} shares @ ${avg_price}")
        print(f"   Description: {desc}")
        print()
else:
    print("\nNo stock orders found from the bot yet.")

print("=" * 100)
