#!/usr/bin/env python3
import requests
import json

requests.packages.urllib3.disable_warnings()

response = requests.get("https://localhost:5055/v1/api/iserver/account/orders", verify=False)
data = response.json()

print("\nRecent Orders:")
print("=" * 80)

for order in data.get('orders', [])[:10]:
    ticker = order.get('ticker', 'N/A')
    desc = order.get('orderDesc', 'N/A')
    status = order.get('status', 'N/A')
    order_id = order.get('orderId', 'N/A')
    print(f"ID: {order_id} | {ticker:8} | {desc:50} | {status}")
