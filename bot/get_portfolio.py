#!/usr/bin/env python3
import requests
import json

requests.packages.urllib3.disable_warnings()

response = requests.get("https://localhost:5055/v1/api/portfolio/DUP158699/positions/0", verify=False)
positions = response.json()

print("\nYour Portfolio:")
print("=" * 80)
for p in positions:
    ticker = p.get('ticker', 'N/A')
    position = p.get('position', 0)
    conid = p.get('conid', 0)
    asset_class = p.get('assetClass', 'N/A')
    mkt_value = p.get('mktValue', 0)
    print(f"{ticker:8} | Qty: {position:12} | ConID: {conid:10} | Type: {asset_class:8} | Value: ${mkt_value:,.2f}")
