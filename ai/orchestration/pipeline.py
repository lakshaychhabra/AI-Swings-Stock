import json, os
from datetime import date
from ai.agents.sentiment_agent import news_agent
from ai.agents.ta_agent import ta_agent
from ai.agents.ensemble_agent import combine_signals

NEWS_CACHE = "data/news_cache.json"

def load_news(ticker: str):
    today = str(date.today())

    if os.path.exists(NEWS_CACHE):
        with open(NEWS_CACHE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    if ticker in data and data[ticker]["date"] == today:
        return data[ticker]  # cached
    else:
        state = news_agent.invoke({"topic": f"is {ticker} stock buy or sell"})
        news_result = {
            "date": today,
            "news": state["news"],
            "decision": state["decision"],
            "reason": state["reason"]
        }
        data[ticker] = news_result

        os.makedirs(os.path.dirname(NEWS_CACHE), exist_ok=True)
        with open(NEWS_CACHE, "w") as f:
            json.dump(data, f, indent=2)

        return news_result
    
def get_ta_decision(ticker: str):
    return ta_agent.invoke({"ticker": ticker})

def analyse_ticker(request: dict):
    ticker = request.get("ticker")
    if not ticker:
        return {"error": "Missing 'ticker'"}

    news_result = load_news(ticker)
    ta_decision = get_ta_decision(ticker)
    final_decision = combine_signals(news_result, ta_decision)

    return {
        "ticker": ticker,
        "news_decision": news_result,
        "ta_decision": ta_decision,
        "final_decision": final_decision
    } 