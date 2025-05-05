import json, os
from datetime import date
from agents.sentiment_agent import news_agent
from agents.ta_agent import ta_agent
from agents.ensemble_agent import combine_signals
from agents.risk_agent import risk_agent
from core.technical_analysis.fetch_data import fetch_data
from core.utils.utlis import clean_ta
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
    
def get_ta_decision(technical_data):
    return ta_agent.invoke(technical_data)

def get_risk_decision(technical_data):
    return risk_agent.invoke(technical_data)

def analyse_ticker(request: dict):
    ticker = request.get("ticker")
    if not ticker:
        return {"error": "Missing 'ticker'"}

    technical_data = fetch_data({"ticker": ticker})

    print("Running News Agent")
    # news_result = load_news(ticker)
    print("Running TA Agent")
    ta_decision = get_ta_decision(technical_data)
    print("Running Risk Agent")
    # risk_decision = get_risk_decision(technical_data)
    print("Ensembling Signals")

    # print(news_result)
    # print(ta_decision)
    # print(risk_decision)
    # final_decision = combine_signals(news_result, ta_decision, risk_decision)
    # print(final_decision)

    print(ta_decision)

    ta_decision_cleaned = clean_ta(ta_decision)
    # print(ta_decision)
    return json.dumps({
        "ticker": ticker,
        # "news_decision": news_result,
        "ta_decision": ta_decision_cleaned,
        # "risk_decision": risk_decision,
        # "final_decision": final_decision
    }, default=str)