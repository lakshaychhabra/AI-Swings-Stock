# 📈 AI-Swings-Stock

![GitHub Repo stars](https://img.shields.io/github/stars/lakshaychhabra/AI-Swings-Stock?style=social)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)

AI-Swings-Stock is an intelligent stock trading system designed to automate stock selection, perform in-depth AI analysis, and execute buy/sell operations via broker APIs.

It is engineered to focus on **swing trading** opportunities using a combination of qualitative, quantitative, sentiment, and risk-based analysis powered by AI agents.

---

## 🚀 Project Overview

- **Cron Agent**: Automatically fetches and builds a daily wishlist of promising stocks based on news, volume analysis, trackers, and articles.
- **AI Agentic Analysis**: Performs multi-dimensional evaluation for each shortlisted stock — combining qualitative, quantitative, sentiment, strategy, risk, and stock metrics analysis.
- **System Execution (SE)**: Executes buy/sell/hold actions through Zerodha, maintains ledgers, tracks PnL, and generates dashboards with real-time alerts via Telegram.

---

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
|  Execution via Broker     |
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

| Layer         | Technology                          |
|---------------|-------------------------------------|
| Backend       | Python, Golang                      |
| Agents        | Langgraph                           |
| Database      | MongoDB                             |
| Broker API    | yfinance / Zerodha KiteConnect      |
| Alerting      | Telegram Bot API                    |
| Logging       | File-based logs                     |
| LLM           | Gemini Free Version                 |

## License

MIT License

Copyright (c) 2025 Lakshay Chhabra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

