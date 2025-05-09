# 📈 Market Technicals with Python

A comprehensive, code-rich collection of Jupyter notebooks and Python scripts for performing **technical analysis**, **trend detection**, and **machine learning modeling** on cryptocurrency data using the Binance exchange API.

---

## 🎯 Purpose

To empower developers and data scientists to:
- Fetch and analyze real-time crypto market data
- Apply rule-based and ML-driven strategies
- Backtest margin-trading logic
- Visualize uptrends, entry points, and opportunities

---

## 🧠 Core Capabilities

- 📊 Real-time ticker, kline (candlestick), and trade data extraction
- 🧠 Deep Learning models (Bi-directional LSTM) for price/volume forecasting
- 📈 Margin trading signal generation with customizable thresholds
- 📍 Uptrend tracking on 15-minute intervals for BTC, ETH, and altcoins
- 📉 Strategy comparison: baseline, V1/V2/V5/V6 runnable versions

---

## 🗃️ File & Feature Overview

| Module / Notebook                                          | Description                                      |
|------------------------------------------------------------|--------------------------------------------------|
| `fetcher.py`                                               | Pulls historical market data from Binance API    |
| `kline.ipynb`, `tickers.ipynb`                             | Exploratory visualization of candle and ticker data |
| `Binance-Capture-UpTrend-15mins-*.ipynb/.py`               | Detects bullish trends at 15m granularity        |
| `Binance-Capture-Margin-Trading-V*.ipynb/.py`              | Simulates & tests margin trading logic           |
| `AI-Binance-Bi-Direction-LSTM-OnlyPriceInput.ipynb`        | LSTM-based forecasting using closing prices      |
| `AI-Binance-Bi-Direction-LSTM-InputVolume-OutputPrice-*.ipynb` | Models relationship between volume and price |
| `exchangeinfo.py`                                          | Prints supported symbols and markets on Binance  |

---

## 🧪 Requirements

- Python 3.8+
- Binance API Key (for authenticated endpoints if needed)
- Libraries:
  ```bash
  pip install pandas numpy matplotlib python-binance scikit-learn tensorflow keras
  ```

---

## 🚀 Example Use

### 1. View BTC 15-min Uptrend Signal

```bash
python Binance-Capture-UpTrend-15mins-Tradable-Go-Live-Test-V6.py
```

### 2. Run LSTM Forecasting Notebook

```bash
jupyter notebook AI-Binance-Bi-Direction-LSTM-OnlyPriceInput.ipynb
```

### 3. Pull Ticker Info

```bash
python fetcher.py
```

---

## 📊 Sample Output (JSON)

```json
{
  "symbol": "BTCUSDT",
  "trend": "uptrend",
  "signal_strength": 87.6,
  "last_price": 41987.22,
  "recommendation": "BUY"
}
```

---

## 🧩 Ideas for Extension

- Telegram or Discord bot for live alerts
- Real-time WebSocket feeds
- Deployment via Docker or Streamlit UI
- Model retraining pipeline with new market data

---

## 📁 Folder Highlights

```
.
├── AI-Binance-*.ipynb           # LSTM forecasting
├── Binance-Capture-*.ipynb/.py  # Uptrend/margin trading strategies
├── fetcher.py                   # Market data retrieval
├── tickers.ipynb                # Symbol and ticker info
├── exchangeinfo.py              # Print market listings
└── README.md
```

---

