from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langchain_core.runnables import RunnableLambda
from technical_analysis.technical_workflow import run_technical_analysis
from langchain.prompts import ChatPromptTemplate
import yfinance as yf
from llm.llm import llm


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
    result = {"candles": {}, "15m_indicators": {}, "ticker": ticker, "history": state.get("history", [])}

    for p in periods:
        df = yf.download(ticker, interval=p, period="1d")
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]
        df = df.drop(columns=['adj_close'], errors='ignore')
        result["candles"][p] = df.tail(5).to_dict(orient="records")

        if p == "15m":
            result["15m_indicators"] = run_technical_analysis(df)

    return result

prompt = ChatPromptTemplate.from_template("""
You're a stock trading assistant.
Given the following market data, decide whether to Buy / Sell / Hold the stock.

Ticker: {ticker}
Candlestick Data:
{candles}

Technical Indicators:
{indicators}

Past Decisions:
{history}

Answer:
- Decision: <Buy/Sell/Hold>
- Reason (detailed): <explanation>
""")

def llm_decision(state: TradeState) -> TradeState:
    messages = prompt.format_prompt(
        ticker=state["ticker"],
        candles=state["candles"],
        indicators=state["indicators"],
        history=state.get("history", [])
    ).to_messages()

    response = llm.invoke(messages)
    text = response.content.strip()

    if "Buy" in text:
        decision = "Buy"
    elif "Sell" in text:
        decision = "Sell"
    else:
        decision = "Hold"

    return {**state, "decision": decision, "reason": text}

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

app = graph.compile()
