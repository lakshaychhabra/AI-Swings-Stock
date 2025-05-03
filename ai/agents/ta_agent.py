from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.runnables import RunnableLambda
from core.technical_analysis.technical_workflow import run_technical_analysis
from langchain.prompts import ChatPromptTemplate
import yfinance as yf
from ai.llm.gemini import llm, TradeDecision
from typing import Annotated


class TradeState(TypedDict):
    candles: dict
    indicators: dict
    history: List[str]
    decision: Optional[str]
    reason: Optional[str]
    ticker: str



def fetch_data(state: TradeState) -> TradeState:
    ticker = state["ticker"]
    periods = ["5m", "15m", "30m", "60m"]
    result = {"candles": {}, "indicators": {}, "ticker": ticker, "history": state.get("history", [])}

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

        if p == "15m":
            try:
                result["indicators"] = run_technical_analysis(df)
            except Exception as e:
                print(f"Error running TA: {e}")
                result["indicators"] = {}

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


# --- 4. Node: Update History ---
def update_history(state: TradeState) -> TradeState:
    hist = state.get("history", [])
    hist.append(f"{state['decision']}: {state['reason']}")
    return {**state, "history": hist[-5:]}  # retain last 5 reasons

# --- 5. Build LangGraph ---
graph = StateGraph(TradeState)

graph.add_node("fetch_data", RunnableLambda(fetch_data))
graph.add_node("decide", RunnableLambda(llm_decision))
graph.add_node("update", RunnableLambda(update_history))

graph.set_entry_point("fetch_data")
graph.add_edge("fetch_data", "decide")
graph.add_edge("decide", "update")
graph.add_edge("update", END)

ta_agent = graph.compile()
