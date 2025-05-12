import json, os
from datetime import date
from agents.sentiment_agent import news_agent
from agents.ta_agent import ta_agent
from agents.ensemble_agent import combine_signals
from agents.risk_agent import risk_agent
from core.technical_analysis.fetch_data import fetch_data
from core.utils.utlis import clean_ta
import time
import requests
from fastapi.responses import JSONResponse
from core.utils.utlis import safe_json

session = requests.Session()

NEWS_CACHE = "data/news_cache.json"

cache_ticker_testing = {}

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

    try:
        tat = {}

        t0 = time.time()
        print("Fetching Technical Data")

        if cache_ticker_testing.get("ticker"):
            technical_data = cache_ticker_testing.get("ticker")
            print("Using cached technical data")
        else:
            technical_data = fetch_data({"ticker": ticker})
            cache_ticker_testing[ticker] = technical_data
            print("Fetched technical data from source")

        if len(technical_data["candles"]) == 0:
            return {"error": "Failed to fetch technical data"}
        
        tat["fetch_data"] = round(time.time() - t0, 3)
        print(technical_data)

        print("Running News Agent")
        t1 = time.time()
        news_result = load_news(ticker)
        tat["news_agent"] = round(time.time() - t1, 3)

        print("Running TA Agent")
        t2 = time.time()
        ta_decision = get_ta_decision(technical_data)
        tat["ta_agent"] = round(time.time() - t2, 3)

        print("Running Risk Agent")
        t3 = time.time()
        risk_decision = get_risk_decision(technical_data)
        tat["risk_agent"] = round(time.time() - t3, 3)

        print("Ensembling Signals")
        t4 = time.time()
        final_decision = combine_signals(news_result, ta_decision, risk_decision)
        tat["combine_signals"] = round(time.time() - t4, 3)

        ta_decision_cleaned = clean_ta(ta_decision)
        tat["TAT"] = round(time.time() - t0, 3)

        details = {
            "ticker": ticker,
            "news_decision": news_result,
            "ta_decision": ta_decision_cleaned,
            "risk_decision": risk_decision,
            "final_decision": final_decision,
        }
        
        # return JSONResponse(content=json.loads(safe_json({"details": details, "tat": tat})))
        return json.dumps({
            "details": details,
            "tat": tat
        }, default=str)
    except Exception as error:
        print(error)
        import traceback
        return {"error": error, "error_details": str(traceback.format_exc())}