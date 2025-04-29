## 🤖 Agentic Decision Guide Table

| **Indicator** | **Agent Trigger Condition** | **Action** | **Use Case** |
|:--------------|:-----------------------------|:----------|:-------------|
| **RSI** | RSI > 70 | Consider Sell | Overbought zone, possible reversal |
|  | RSI < 30 | Consider Buy | Oversold zone, possible bounce |
|  | RSI crosses above 50 | Confirm Long Bias | Momentum turning bullish |
| **Stochastic K/D** | %K crosses %D from below (<20) | Buy Signal | Fast oversold reversal |
|  | %K crosses %D from above (>80) | Sell Signal | Fast overbought exit |
| **MACD** | MACD crosses above Signal | Buy Signal | Bullish momentum crossover |
|  | MACD crosses below Signal | Sell Signal | Bearish momentum crossover |
| **Awesome Oscillator** | AO crosses above 0 | Buy Bias | Momentum turning positive |
|  | AO crosses below 0 | Sell Bias | Momentum turning negative |
| **Rate of Change (ROC)** | ROC > 0 and rising | Confirm Entry | Price accelerating upward |
|  | ROC < 0 and falling | Confirm Exit | Price momentum weakening |
| **EMA** | EMA 9 > EMA 21 | Uptrend | Confirm long positions |
|  | EMA 9 < EMA 21 | Downtrend | Confirm short positions |
| **PSAR** | PSAR flips below price | Buy | Trailing stop reverses to long |
|  | PSAR flips above price | Sell | Trailing stop reverses to short |
| **Ichimoku (Tenkan/Kijun)** | Tenkan crosses Kijun upward | Bullish Signal | Short-term bullish reversal |
|  | Tenkan crosses Kijun downward | Bearish Signal | Short-term bearish reversal |
| **Bollinger Bands** | Price breaks above upper band | Caution: Overextension | May indicate short-term pullback |
|  | Price breaks below lower band | Consider Long | Possible bounce from volatility overshoot |
| **ATR** | ATR rising | Expand SL / Volatility increasing | Use dynamic stops |
|  | ATR falling | Tighten SL / Low volatility | Choppy market |
| **VWAP** | Price > VWAP | Long Bias | Institution support area |
|  | Price < VWAP | Short Bias | Below average trade price |
| **OBV** | OBV rising with price | Confirm Long | Price rise supported by volume |
|  | OBV falling with price | Confirm Short | Weak structure |
| **Mass Index** | Mass Index > 27 | Trend Reversal Likely | Tighten SL or prepare to flip |
| **Ulcer Index** | Ulcer Index > 3.5 | Risk too high | Avoid entry or reduce size |
| **KAMA** | Close > KAMA and KAMA rising | Trend Confirmed Long | Adaptive support |
|  | Close < KAMA and KAMA falling | Trend Confirmed Short | Adaptive resistance |

---

## 🧠 Notes for Agent Logic
- Combine multiple signals for higher confidence.  
  Example: RSI < 30 **and** Price < VWAP → Strong Long Entry
- Consider adding a **cooldown timer** after entries to avoid false flips.
- Use **ATR** to size SL and adjust trade duration risk.
- Use **Ulcer Index** only if holding > 3 candles (i.e., >30 mins) to reassess drawdown pain.

---

## 📌 Suggested Thresholds (can be tuned by agent)
- RSI: 30/50/70
- Stoch K: 20/80
- MACD: Zero line and signal crossover
- Mass Index: >27 = reversal
- Ulcer Index: >3.5 = high stress
- VWAP: Entry only when price is above VWAP for Longs

