# BTC Trading Bot

Monitors Bitcoin price from Binance and places trades on Interactive Brokers based on BTC price movements.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure IBKR Gateway is running:
```bash
cd ..
docker-compose up
```

3. Login to IBKR Gateway at https://localhost:5055

## Bots Available

### 1. BTC Monitor (Read-only)

Just monitors BTC price without trading:

```bash
python btc_monitor.py
```

Displays:
- Current BTC price
- 24h high/low
- 24h price change percentage
- 24h trading volume

Updates every 10 seconds.

### 2. BTC Trading Bot (Live Trading)

⚠️ **WARNING: This bot places REAL orders on your IBKR account!**

```bash
export IBKR_ACCOUNT_ID="YOUR_ACCOUNT_ID"
python btc_trading_bot.py
```

**Trading Strategy:**
- When BTC > $68,000 → BUY 1 share of AAPL
- When BTC < $66,000 → SELL all AAPL shares
- Checks every 30 seconds

**Customization:**

Edit these variables in `btc_trading_bot.py`:
```python
BTC_THRESHOLD_UP = 68000      # Buy trigger price
BTC_THRESHOLD_DOWN = 66000    # Sell trigger price
STOCK_CONID = 265598          # Stock to trade (AAPL)
TRADE_QUANTITY = 1            # Number of shares
```

## Safety Features

- Bot checks your current positions before trading
- Won't buy if you already have a position
- Won't sell if you don't have a position
- Requires manual confirmation before starting

## Next Steps

- Add more sophisticated indicators (RSI, moving averages)
- Implement stop-loss and take-profit
- Add multiple trading pairs
- Log trades to a database
- Send notifications (email/SMS) on trades
