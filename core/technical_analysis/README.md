# 📄 README.md

## 📈 Momentum Indicators

| **Function** | **Description** |
|:-------------|:----------------|
| `calculate_rsi(close, window=14)` | Detects overbought (>70) and oversold (<30) zones quickly. Useful for identifying potential short-term reversals. |
| `calculate_stochastic(high, low, close, window=14, smooth_window=3)` | Identifies fast reversal points by comparing close price to recent price ranges. |
| `calculate_macd(close, window_slow=26, window_fast=12, window_sign=9)` | Captures trend direction and momentum shifts via fast-slow moving average crossovers. |
| `calculate_williams_r(high, low, close, window=14)` | Measures overbought/oversold conditions relative to recent highs and lows. |
| `calculate_awesome_oscillator(high, low, window1=5, window2=34)` | Detects fast momentum changes based on median price difference over two periods. |
| `calculate_roc(close, window=12)` | Measures speed and magnitude of recent price changes — useful for breakout detection. |

---

## 📈 Trend Indicators

| **Function** | **Description** |
|:-------------|:----------------|
| `calculate_ema(close, window=9)` | Smooths out short-term price noise; reacts faster to price changes compared to SMA. |
| `calculate_macd_trend(close, window_slow=26, window_fast=12, window_sign=9)` | Identifies trend direction and momentum using MACD logic. |
| `calculate_psar(high, low, close)` | Trailing stop-loss indicator; flips position when trend changes. |
| `calculate_ichimoku(high, low)` | Generates dynamic support and resistance using Tenkan-sen and Kijun-sen lines. |

---

## 📈 Volatility Indicators

| **Function** | **Description** |
|:-------------|:----------------|
| `calculate_bollinger_bands(close, window=20, window_dev=2)` | Identifies volatility expansions/contractions and squeeze breakout setups. |
| `calculate_atr(high, low, close, window=14)` | Measures market volatility; useful for setting dynamic stop-loss or position sizing. |

---

## 📈 Volume Indicators

| **Function** | **Description** |
|:-------------|:----------------|
| `calculate_vwap(high, low, close, volume)` | Calculates volume-weighted average price; acts as intraday dynamic support/resistance. |
| `calculate_obv(close, volume)` | Measures buying/selling pressure through cumulative volume flows. Useful for confirming trend strength. |

---

## 📈 Adaptive / Risk Management Indicators

| **Function** | **Description** |
|:-------------|:----------------|
| `calculate_mass_index(high, low, window=25)` | Detects potential trend reversals by analyzing range expansions and contractions. |
| `calculate_ulcer_index(close, window=14)` | Measures downside risk by quantifying depth and duration of drawdowns. |
| `calculate_kama(close, window=10, fastend=2/3, slowend=2/31)` | Adaptive moving average that dynamically adjusts speed based on trend strength and volatility. |

---

## ⚙️ General Notes

- All functions are **pure** (no side effects), making them **easy to integrate** into agentic decision flows.
- Return types are either `pd.Series` or `pd.DataFrame` depending on the number of outputs.
- Parameters like window size, smoothing, fast/slow periods can be tuned dynamically by agents based on market conditions.

