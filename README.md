# 📈 AI-Swings-Stocks

AI-Swings-Stocks is an intelligent stock trading system designed to automate stock selection, perform in-depth AI analysis, and execute buy/sell operations via broker APIs.

It is engineered to focus on **swing trading** opportunities using a combination of qualitative, quantitative, sentiment, and risk-based analysis powered by AI agents.

---

## 🚀 Project Overview

- **Cron Agent**: Automatically fetches and builds a daily wishlist of promising stocks based on news, volume analysis, trackers, and articles.
- **AI Agentic Analysis**: Performs multi-dimensional evaluation for each shortlisted stock — combining qualitative, quantitative, sentiment, strategy, risk, and stock metrics analysis.
- **System Execution (SE)**: Executes buy/sell/hold actions through Zerodha, maintains ledgers, tracks PnL, and generates dashboards with real-time alerts via Telegram.

---

## 🛠️ Architecture

## 🛠️ Architecture Flow (ASCII Style)
```
+----------------------+
|  Scheduler (Cron)     |
+----------------------+
            ↓
+----------------------+
|  Wishlist Creation    |
+----------------------+
            ↓
+-----------------------------+
|  AI Multi-Agent Analysis     |
+-----------------------------+
            ↓
+-------------------------------------+
|  Trade Decision (Buy / Sell / Hold) |
+-------------------------------------+
            ↓
+---------------------------+
|  Execution via Zerodha    |
+---------------------------+
            ↓
+----------------------------+
|  PnL and Ledger Updates    |
+----------------------------+
            ↓
+-----------------------+
|  Dashboards and Alerts |
+-----------------------+


```
---

## 📚 Components

### 1. Cron Agent
- Fetch top 10 stocks daily
- Source: News articles, volume trackers, financial sources
- Update the Wishlist table

### 2. AI Agentic Analysis
- Perform stock evaluations across multiple AI modules:
  - Qualitative Analysis
  - Quantitative Analysis
  - Sentiment Analysis
  - Strategy Analysis
  - Risk Analysis
  - Stock Number Analysis
  - Combination Aggregator

### 3. System Execution (SE)
- Buy/Sell/Hold stocks via Zerodha KiteConnect API
- Manage Ledger of trades
- Track and compute PnL (Daily/Weekly/Monthly/Lifetime)
- Maintain Instrumentation Logs
- Send Buy/Sell/Balance alerts to Telegram

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| Backend | Python (FastAPI, Streamlit) |
| Scheduling | AWS Lambda / Google Cloud Scheduler |
| Database | PostgreSQL / Redis |
| Broker API | Zerodha KiteConnect |
| Alerting | Telegram Bot API |
| Logging | ElasticSearch or File-based logs |
| Hosting | Render / Railway / AWS Lightsail |

# Technical Analysis Library

A comprehensive Python library for technical analysis of financial market data. This library provides a collection of technical indicators commonly used in financial markets.

## Installation

```bash
pip install -r requirements.txt
```

## Features

The library includes the following categories of technical indicators:

### Volume Indicators
- Accumulation/Distribution (A/D)
- On-Balance Volume (OBV)
- Chaikin Money Flow (CMF)
- Force Index (FI)
- Ease of Movement (EoM)
- Volume Price Trend (VPT)

### Momentum Indicators
- Relative Strength Index (RSI)
- Stochastic Oscillator
- Moving Average Convergence Divergence (MACD)
- Williams %R
- Awesome Oscillator (AO)
- Rate of Change (ROC)

### Trend Indicators
- Average Directional Movement Index (ADX)
- Mass Index
- Triple Exponential Average (TRIX)
- Vortex Indicator

### Volatility Indicators
- Bollinger Bands
- Average True Range (ATR)
- Donchian Channel
- Keltner Channel

### Other Indicators
- Daily Return
- Daily Log Return
- Cumulative Return

## Usage Example

```python
import pandas as pd
from technical_analysis.momentum import RSIIndicator
from technical_analysis.volatility import BollingerBands

# Load your data
df = pd.DataFrame({
    'Close': [...],  # your close prices
    'High': [...],   # your high prices
    'Low': [...],    # your low prices
    'Volume': [...]  # your volume data
})

# Calculate RSI
rsi = RSIIndicator(close=df['Close'])
df['RSI'] = rsi.rsi()

# Calculate Bollinger Bands
bb = BollingerBands(close=df['Close'])
df['BB_middle'] = bb.bollinger_mavg()
df['BB_upper'] = bb.bollinger_hband()
df['BB_lower'] = bb.bollinger_lband()
```

## Requirements

- Python 3.7+
- NumPy >= 1.20.0
- Pandas >= 1.3.0

## License

MIT License

