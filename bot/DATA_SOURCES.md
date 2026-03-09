# Market Data Sources Guide

## 🎯 Summary

You have **3 working data sources** right now:
1. ✅ **Binance API** (Crypto) - FREE, unlimited
2. ✅ **IBKR API** (Stocks/Crypto) - Already connected
3. ✅ **yfinance** (Stocks) - FREE, easy to use

## 📊 Currently Working Sources

### 1. Binance API (Crypto) ✅
**Status**: Already integrated in your bot
**Cost**: FREE
**Data**: BTC, ETH, SOL, LTC, and 300+ other cryptos
**Features**:
- Real-time prices
- 24h statistics
- Historical candlestick data
- Order book data
- No API key needed

**Example**:
```python
import requests
url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
data = requests.get(url).json()
print(f"BTC Price: ${data['lastPrice']}")
```

### 2. IBKR API (Your Gateway) ✅
**Status**: Already connected
**Cost**: FREE (you already have account)
**Data**: Stocks, options, futures, forex, crypto
**Features**:
- Real-time market data
- Historical data
- Order book
- Your actual positions

**Example**:
```python
# Already working in your bot
url = f"https://localhost:5055/v1/api/iserver/marketdata/snapshot?conids={conid}"
```

### 3. yfinance (Yahoo Finance) ✅
**Status**: Easy to install
**Cost**: FREE
**Data**: All US stocks, ETFs, indices
**Installation**: `pip install yfinance`

**Example**:
```python
import yfinance as yf
ticker = yf.Ticker("AAPL")
data = ticker.history(period="1mo")
print(data)
```

## 🆓 Other Free Sources

### 4. Alpha Vantage
**Cost**: FREE (500 calls/day)
**Sign up**: https://www.alphavantage.co/support/#api-key
**Data**: Stocks, forex, crypto, technical indicators
**Best for**: Historical data, technical analysis

```python
import requests
url = "https://www.alphavantage.co/query"
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'AAPL',
    'apikey': 'YOUR_KEY'
}
data = requests.get(url, params=params).json()
```

### 5. Polygon.io
**Cost**: FREE tier (5 calls/min)
**Sign up**: https://polygon.io/
**Data**: Stocks, options, forex, crypto
**Best for**: Real-time data, aggregates

### 6. Finnhub
**Cost**: FREE tier (60 calls/min)
**Sign up**: https://finnhub.io/
**Data**: Stocks, forex, crypto, news
**Best for**: News sentiment, earnings data

### 7. IEX Cloud
**Cost**: FREE tier available
**Sign up**: https://iexcloud.io/
**Data**: US stocks, real-time quotes
**Best for**: Real-time US market data

## 💰 Paid Sources (Better Quality)

### 1. Alpaca Markets
**Cost**: FREE paper trading, $99/mo live
**Website**: https://alpaca.markets/
**Best for**: Algorithmic trading, real-time data

### 2. Quandl
**Cost**: Varies by dataset
**Website**: https://www.quandl.com/
**Best for**: Financial/economic data, fundamentals

### 3. Bloomberg Terminal
**Cost**: $24,000/year
**Best for**: Professional traders (overkill for most)

## 🔧 Recommended Setup for Your Bot

### For Crypto Trading:
✅ **Use Binance API** (already working)
- Free, unlimited
- Best crypto data available
- Real-time updates

### For Stock Trading:
✅ **Option 1: yfinance** (easiest)
```bash
pip install yfinance
```

✅ **Option 2: Alpha Vantage** (more features)
1. Get free API key: https://www.alphavantage.co/support/#api-key
2. 500 calls/day limit
3. Technical indicators included

✅ **Option 3: IBKR API** (already have it)
- Use your existing gateway
- Real-time data
- No extra setup needed

## 📝 Installation Instructions

### Install yfinance (Recommended):
```bash
cd interactive-brokers-web-api/bot
pip install yfinance
```

### Install Alpha Vantage:
```bash
pip install alpha-vantage
```

### Install Polygon:
```bash
pip install polygon-api-client
```

## 🎯 What I Recommend

For your current bot, I recommend:

1. **Keep Binance** for crypto (already working perfectly)
2. **Add yfinance** for stocks (free, easy, no API key)
3. **Use IBKR API** as backup (you already have it)

This gives you:
- ✅ Free data
- ✅ No API key management
- ✅ Real-time updates
- ✅ Historical data
- ✅ Technical indicators

## 🚀 Next Steps

Want me to:
1. Install yfinance and integrate it into your bot?
2. Set up Alpha Vantage with API key?
3. Add more technical indicators using the data?
4. Create a data aggregator that combines multiple sources?

Let me know what you'd like!
