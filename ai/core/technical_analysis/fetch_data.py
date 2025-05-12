from typing import TypedDict, List, Optional
import yfinance as yf
from core.technical_analysis.technical_workflow import run_technical_analysis
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
from kiteconnect import KiteConnect
from config.env import ZERODHA_API_KEY, ZERODHA_API_SECRET, ZERODHA_TOKEN
class TradeState(TypedDict):
    candles: dict
    indicators: dict
    history: List[str]
    latest_volume: Optional[float]

kite = KiteConnect(api_key=ZERODHA_API_KEY)
kite.set_access_token(ZERODHA_TOKEN)

INSTRUMENT_MAP = {
    "RELIANCE": 738561,
    "INFY": 408065,
    "TCS": 2953217,
    "HDFCBANK": 500180
    # Add more as needed
}

def fetch_data_yfinance(state: TradeState) -> TradeState:
    
    ticker = state["ticker"]
    periods = ["5m", "15m", "30m", "60m"]
    result = {
        "candles": {},
        "indicators": {},  # will contain nested indicators
        "ticker": ticker,
        "history": state.get("history", []),
        "latest_volume": None,
    }

    # Step 1: Fetch average volume over 30 days
    try:
        session = requests.Session(impersonate="chrome")
        hist_df = yf.Ticker(ticker, session=session).history(period="35d")
        hist_df = hist_df.dropna(subset=["Volume"])
        avg_volume_30d = hist_df.tail(30)["Volume"].mean()
        result["indicators"]["avg_volume_30d"] = avg_volume_30d
    except Exception as e:
        print(f"Error fetching avg_volume_30d: {e}")
        result["indicators"]["avg_volume_30d"] = None
        avg_volume_30d = None

    # Step 2: Download intraday candles and compute indicators
    for p in periods:
        try:
            df = yf.download(ticker, interval=p, period="5d", group_by="column")  # ⬅️ increased period
            if df.empty:
                continue

            df.columns = [
                col[0].lower().replace(" ", "_") if isinstance(col, tuple) else col.lower().replace(" ", "_")
                for col in df.columns
            ]
            df = df.drop(columns=["adj_close"], errors="ignore")

            # Save only last 5 rows for display
            result["candles"][p] = df.tail(5).to_dict(orient="records")

            # Save latest volume from 15m
            if p == "15m" and len(df) >= 1:
                result["latest_volume"] = df.iloc[-1]["volume"]

            # Step 3: Run technical analysis (on full df)
            if p in ["15m", "60m"] and len(df) >= 30:
                try:
                    result["indicators"][p] = run_technical_analysis(
                        df,
                        latest_volume=result.get("latest_volume") if p == "15m" else None,
                        avg_volume_30d=avg_volume_30d
                    )
                except Exception as e:
                    print(f"Error running TA on {p}: {e}")
                    result["indicators"][p] = {}
            else:
                if p in ["15m", "60m"]:
                    print(f"Skipped TA on {p} — not enough data ({len(df)} rows)")
                    result["indicators"][p] = {}

        except Exception as e:
            print(f"Error fetching or processing {p} data: {e}")

    return result

def fetch_kite_candles(token: int, interval: str, days: int) -> pd.DataFrame:
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days)
    
    data = kite.historical_data(
        instrument_token=token,
        from_date=from_date,
        to_date=to_date,
        interval=interval,
        continuous=False
    )
    
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
    return df


def fetch_data(state: dict) -> dict:
    symbol = state["ticker"]
    token = INSTRUMENT_MAP.get(symbol)

    if token is None:
        raise ValueError(f"Instrument token for {symbol} not found")

    periods = {
        "5minute": 5,
        "15minute": 5,
        "30minute": 5,
        "60minute": 5
    }

    result = {
        "candles": {},
        "indicators": {},
        "ticker": symbol,
        "history": state.get("history", []),
        "latest_volume": None,
    }

    # Step 1: Fetch average daily volume (35 days)
    try:
        df_daily = fetch_kite_candles(token, "day", 35)
        avg_volume_30d = df_daily.tail(30)["volume"].mean()
        result["indicators"]["avg_volume_30d"] = avg_volume_30d
    except Exception as e:
        print(f"Error fetching avg_volume_30d: {e}")
        result["indicators"]["avg_volume_30d"] = None
        avg_volume_30d = None

    # Step 2: Fetch intraday candles
    for interval, lookback_days in periods.items():
        try:
            df = fetch_kite_candles(token, interval, lookback_days)
            if df.empty:
                continue

            df = df.dropna()
            df = df.rename(columns=str.lower)

            # Save last 5 candles
            result["candles"][interval] = df.tail(5).to_dict(orient="records")

            if interval == "15minute" and len(df) >= 1:
                result["latest_volume"] = df.iloc[-1]["volume"]

            if interval in ["15minute", "60minute"] and len(df) >= 30:
                try:
                    result["indicators"][interval] = run_technical_analysis(
                        df,
                        latest_volume=result.get("latest_volume") if interval == "15minute" else None,
                        avg_volume_30d=avg_volume_30d
                    )
                except Exception as e:
                    print(f"TA error on {interval}: {e}")
                    result["indicators"][interval] = {}
            else:
                result["indicators"][interval] = {}

        except Exception as e:
            print(f"Error fetching {interval} data: {e}")

    return result