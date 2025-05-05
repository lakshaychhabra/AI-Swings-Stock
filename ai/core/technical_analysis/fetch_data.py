from typing import TypedDict, List, Optional
import yfinance as yf
from core.technical_analysis.technical_workflow import run_technical_analysis

class TradeState(TypedDict):
    candles: dict
    indicators: dict
    history: List[str]
    latest_volume: Optional[float]

def fetch_data(state: TradeState) -> TradeState:
    
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
        hist_df = yf.Ticker(ticker).history(period="35d")
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
