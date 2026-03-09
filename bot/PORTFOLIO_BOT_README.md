# Multi-Asset Portfolio Trading Bot

## Overview
This bot monitors and trades ALL positions in your IBKR portfolio automatically. It analyzes each asset and makes trading decisions based on technical indicators and market momentum.

## Your Current Portfolio (27 positions)
- **Crypto**: BTC, ETH, LTC, SOL
- **Stocks**: NVDA, TSLA, AAPL, UBER, NIO, MSTR, SCHD, SQQQ, SOXS, BLK, BSV, and more
- **ETFs**: XLE, IAU, VTEB, SGOV, MUNY, FXF, FXY, UUP, BX

## Features
- ✅ Monitors all 27 positions in real-time
- ✅ Different strategies for crypto vs stocks
- ✅ Handles both long and short positions
- ✅ Position-based sizing (trades 5% of position value)
- ✅ Minimum trade value of $100
- ✅ Checks every 30 seconds
- ✅ Crypto momentum strategy (Binance data)
- ✅ Automatic order placement

## Trading Strategy

### Crypto (BTC, ETH, LTC, SOL)
- Uses Binance 24h price change data
- **BUY Signal**: Price up > 2% in 24h
- **SELL Signal**: Price down > 2% in 24h
- **HOLD**: Price change between -2% and +2%

### Stocks
- Currently set to HOLD (you can customize)
- Can add RSI, moving averages, or other indicators

## How to Use

### 1. Test Mode (Recommended First)
```bash
python3 interactive-brokers-web-api/bot/test_portfolio_bot.py
```
This will analyze your portfolio without placing any trades.

### 2. Live Trading Mode
```bash
python3 interactive-brokers-web-api/bot/portfolio_bot.py
```
Type `yes` when prompted to start live trading.

### 3. Stop the Bot
Press `Ctrl+C` at any time to stop.

## Configuration

Edit `portfolio_bot.py` to customize:

```python
TRADE_PERCENT = 0.05  # Trade 5% of position size
MIN_TRADE_VALUE = 100  # Minimum $100 per trade
CHECK_INTERVAL = 30  # Check every 30 seconds
```

## Current Analysis Results

Based on latest run:
- **BTC**: BUY signal (up 2.83% in 24h)
- **ETH**: BUY signal (up 4.53% in 24h)
- **SOL**: BUY signal (up 4.33% in 24h)
- **All stocks**: HOLD

## Safety Features
- Skips futures positions (like JGB)
- Skips positions < $100 value
- Only trades when signal changes
- Validates orders before submission
- Handles crypto vs stock order types correctly

## Order Types
- **Crypto**: Market orders with cashQty, IOC time-in-force
- **Stocks**: Market orders with quantity, DAY time-in-force

## Example Output
```
📊 Monitoring 26 positions:

📈 BTC      | Pos:     0.3876 | Value: $   26,656.98 | Type: CRYPTO
   💡 Strong upward momentum (+2.83%)
   🎯 Signal: BUY
   🔔 Signal changed from None to BUY
   🟢 BUY $1332.85 worth of BTC
   ✅ Order placed: BUY BTC
```

## Customization Ideas

### Add More Indicators
You can enhance the `analyze_asset()` method with:
- RSI (Relative Strength Index)
- Moving averages (SMA, EMA)
- MACD
- Volume analysis
- Support/resistance levels

### Adjust Thresholds
Change the momentum thresholds:
```python
if change > 2:  # Change to 1 for more aggressive, 5 for conservative
    return 'BUY', reasons
```

### Add Stock Analysis
Currently stocks are set to HOLD. You can add:
- Fetch stock data from Yahoo Finance or Alpha Vantage
- Calculate technical indicators
- Implement mean reversion or trend following strategies

## Warning
⚠️ This bot places REAL orders on your IBKR account. Always test thoroughly before running live!

## Files
- `portfolio_bot.py` - Main bot with live trading
- `test_portfolio_bot.py` - Test mode (analysis only)
- `get_portfolio.py` - View your current portfolio
