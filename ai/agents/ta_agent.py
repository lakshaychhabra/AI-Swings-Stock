from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.runnables import RunnableLambda
from core.technical_analysis.technical_workflow import run_technical_analysis
from langchain.prompts import ChatPromptTemplate
import yfinance as yf
from llm.gemini import llm, TradeDecision
from typing import Annotated


class TradeState(TypedDict):
    candles: dict
    indicators: dict
    history: List[str]
    decision: Optional[str]
    reason: Optional[str]
    ticker: str
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
        avg_volume_30d = None
        result["indicators"]["avg_volume_30d"] = None

    # Step 2: Download intraday candles
    for p in periods:
        df = yf.download(ticker, interval=p, period="1d", group_by="column")
        if df.empty:
            continue

        df.columns = [
            col[0].lower().replace(" ", "_") if isinstance(col, tuple) else col.lower().replace(" ", "_")
            for col in df.columns
        ]
        df = df.drop(columns=["adj_close"], errors="ignore")
        result["candles"][p] = df.tail(5).to_dict(orient="records")

        if p == "15m" and not df.empty:
            result["latest_volume"] = df.iloc[-1]["volume"]

        # Step 3: Run technical analysis on 15m and 60m
        if p in ["15m", "60m"]:
            try:
                result["indicators"][p] = run_technical_analysis(
                    df,
                    latest_volume=result.get("latest_volume") if p == "15m" else None,
                    avg_volume_30d=avg_volume_30d
                )
            except Exception as e:
                print(f"Error running TA on {p}: {e}")
                result["indicators"][p] = {}

    return result



prompt = ChatPromptTemplate.from_template("""
    You're a trading assistant. Given the market data, output your decision in **valid JSON**.

    Respond ONLY in the following format:

    ```json
    {{
    "decision": "Buy" | "Sell" | "Hold",
    "reason": "<detailed structured explanation>",
                                          
    }}
    ```

    Ticker: {ticker}

    Candlestick Data:
    {candles}

    Technical Indicators:
    {indicators}

    Past Decisions:
    {history}
""")

def llm_decision(state: TradeState) -> TradeState:
    try:
        messages = prompt.format_prompt(
            ticker=state["ticker"],
            candles=state["candles"],
            indicators=state["indicators"],
            history=state.get("history", [])
        ).to_messages()
        result: TradeDecision = llm.invoke(messages)

        return {
            **state,
            "decision": result.decision,
            "reason": result.reason,
            "success": True
        }
    except Exception as e:
        print(f"Error running TA Agent: {e}")
        return {
            **state,
            "success": False,
            "decision": "None",
            "reason": "Error running TA",
        }

def update_history(state: TradeState) -> TradeState:
    hist = state.get("history", [])
    hist.append(f"{state['decision']}: {state['reason']}")
    return {**state, "history": hist[-5:]}  # retain last 5 reasons


graph = StateGraph(TradeState)

# graph.add_node("fetch_data", RunnableLambda(fetch_data))
graph.add_node("decide", RunnableLambda(llm_decision))
graph.add_node("update", RunnableLambda(update_history))

graph.set_entry_point("decide")
graph.add_edge("decide", "update")
graph.add_edge("update", END)

ta_agent = graph.compile()
