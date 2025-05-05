import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from llm.gemini import llm, TradeDecision
from langgraph.graph import StateGraph, END

def compute_risk_profile(state: dict) -> dict:
    """
    Multi-dimensional risk profiling using 15m + 60m indicators, volume data, and sentiment.
    """
    ticker = state["ticker"]
    indicators = state["indicators"]
    indicators_15m = indicators.get("15m", {})
    indicators_60m = indicators.get("60m", {})
    avg_volume_30d = indicators.get("avg_volume_30d")
    latest_volume = state.get("latest_volume")
    # sentiment = state.get("news_sentiment", 0.0)

    reasons = []
    profile = {
        "volatility_risk": "Unknown",
        "liquidity_risk": "Unknown",
        "momentum_risk": "Unknown",
        # "sentiment_risk": "Unknown",
        "conclusion": "",
        "reasons": []
    }

    atr_15m = indicators_15m.get("atr_norm")
    bb_width_15m = indicators_15m.get("bb_width")
    atr_60m = indicators_60m.get("atr_norm")
    bb_width_60m = indicators_60m.get("bb_width")

    if atr_15m and bb_width_15m and atr_60m and bb_width_60m:
        if atr_15m > 0.025 or atr_60m > 0.02 or bb_width_15m > 2 or bb_width_60m > 1.5:
            profile["volatility_risk"] = "High"
            reasons.append(f"Elevated ATR and BB Width in both 15m and 60m suggest unstable price action.")
        elif atr_15m > 0.015 or atr_60m > 0.015:
            profile["volatility_risk"] = "Medium"
            reasons.append(f"Mild volatility across timeframes (ATR ~{atr_15m:.3f} / {atr_60m:.3f}).")
        else:
            profile["volatility_risk"] = "Low"
            reasons.append("Low ATR and tight BBs → stable market behavior.")

    # 🔹 Liquidity Risk
    if latest_volume and avg_volume_30d:
        volume_spike = latest_volume / max(avg_volume_30d, 1)
        if volume_spike < 0.5:
            profile["liquidity_risk"] = "High"
            reasons.append(f"Latest volume ({latest_volume:.0f}) is <50% of 30d avg ({avg_volume_30d:.0f}).")
        elif volume_spike > 2:
            profile["liquidity_risk"] = "High"
            reasons.append(f"Volume spike of {volume_spike:.2f}x → abnormal trading activity.")
        else:
            profile["liquidity_risk"] = "Low"
            reasons.append(f"Volume ratio is {volume_spike:.2f} → normal liquidity.")

    # 🔹 Momentum Risk
    rsi_15m = indicators_15m.get("rsi")
    macd_cross_15m = indicators_15m.get("macd_crossover")
    macd_cross_60m = indicators_60m.get("macd_crossover")
    ichimoku_cross_15m = indicators_15m.get("ichimoku_cross")
    ichimoku_cross_60m = indicators_60m.get("ichimoku_cross")

    if rsi_15m is not None:
        if rsi_15m > 70 or rsi_15m < 30:
            profile["momentum_risk"] = "High"
            reasons.append(f"RSI at {rsi_15m:.1f} → overbought/oversold risk.")
        elif macd_cross_15m or ichimoku_cross_15m:
            # Confirm momentum on higher timeframe
            if macd_cross_60m or ichimoku_cross_60m:
                profile["momentum_risk"] = "Medium"
                reasons.append("Momentum shift confirmed across 15m and 60m (MACD/Ichimoku crossover).")
            else:
                profile["momentum_risk"] = "Low"
                reasons.append("Early momentum signal on 15m not yet confirmed on 60m.")
        else:
            profile["momentum_risk"] = "Low"
            reasons.append("No reversal or extreme momentum signals detected.")

    # if sentiment <= -0.5:
    #     profile["sentiment_risk"] = "High"
    #     reasons.append(f"Strong negative sentiment ({sentiment:.2f}) → possible headline or event risk.")
    # elif sentiment <= -0.2:
    #     profile["sentiment_risk"] = "Medium"
    #     reasons.append(f"Mild bearish sentiment ({sentiment:.2f})")
    # else:
    #     profile["sentiment_risk"] = "Low"
    #     reasons.append(f"Neutral/positive sentiment ({sentiment:.2f})")

    high_risks = [k for k, v in profile.items() if v == "High" and k.endswith("_risk")]
    if len(high_risks) >= 2:
        profile["conclusion"] = "High overall risk due to multiple elevated signals."
    elif "High" in profile.values():
        profile["conclusion"] = "Moderate to High risk – watch closely."
    else:
        profile["conclusion"] = "Low to Medium risk – favorable conditions."

    profile["ticker"] = ticker
    profile["reasons"] = reasons
    return profile

def format_candle_summary(candles):
    try:
        last = candles[-1]
        return (
            f"Latest close: {last['close']:.2f}, "
            f"Open: {last['open']:.2f}, "
            f"Change: {((last['close'] - last['open']) / last['open']) * 100:.2f}%, "
            f"Volume: {last['volume']:.0f}"
        )
    except:
        return "Not available"
    
decision_prompt = ChatPromptTemplate.from_template("""
You're a trading assistant. Given the risk profile of a stock, decide whether to Buy, Sell, or Hold.

Respond in **valid JSON** format like:
```json
{{
  "decision": "Buy" | "Sell" | "Hold",
  "reason": "<short explanation across risk types>",
}}
```

Here is the risk profile:
Ticker: {ticker}
Volatility Risk: {volatility_risk}
Liquidity Risk: {liquidity_risk}
Momentum Risk: {momentum_risk}
Conclusion: {conclusion}
                                                   
Latest Candle Trends (15m):
{candle_summary}
                                                   
Reasons:
{reasons}
""")

def llm_risk_decision(state):
    try:
        candle_summary = format_candle_summary(state.get("candles", {}).get("15m", []))
        messages = decision_prompt.format_prompt(
            ticker=state.get("ticker"),
            volatility_risk=state.get("volatility_risk"),
            liquidity_risk=state.get("liquidity_risk"),
            momentum_risk=state.get("momentum_risk"),
            # sentiment_risk=state.get("sentiment_risk"),
            conclusion=state.get("conclusion"),
            reasons="\n".join(state.get("reasons", [])),
            candle_summary=candle_summary,
        ).to_messages()

        result: TradeDecision = llm.invoke(messages)
        # parsed = json.loads(result.strip().strip("```json").strip("```"))

        return {
            **state,
            "decision": result.decision,
            "reason": result.reason,
            "success": True,
        }

    except Exception as e:
        print(f"[RISK LLM Parsing Error] {e}")
        return {
            **state,
            "decision": "Hold",
            "reason": "Unable to evaluate",
            "success": False,
        }
    

def create_risk_decision_graph():
    builder = StateGraph(dict)

    builder.add_node("risk_analysis", RunnableLambda(compute_risk_profile))
    builder.add_node("llm_decide", RunnableLambda(llm_risk_decision))

    builder.set_entry_point("risk_analysis")
    builder.add_edge("risk_analysis", "llm_decide")
    builder.add_edge("llm_decide", END)

    return builder.compile()

risk_agent = create_risk_decision_graph()