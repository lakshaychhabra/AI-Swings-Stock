from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from llm.gemini import llm_stock_count
stock_count_prompt = ChatPromptTemplate.from_template(
    """
You are a trading assistant. Given a buy signal for stock {ticker}, your job is to calculate how many stocks to buy, stop loss, and target.
You have the following context:

- Current Price: ₹{current_price}
- Balance Available: ₹{balance}
- Holdings: {holdings}
- Risk Profile: {risk_profile}
- Signal Reasoning: {signal_reason}

Only suggest a buy if conditions are favorable (not overexposed, risk is low/medium).

Respond in this JSON format:

{{
  "reason": "...",
  "ticker": "{ticker}",
  "quantity": ...,
  "expected_profit": ...,
  "stop_loss": ...,
  "target": ...
}}
"""
)


def build_stock_count_agent():
    def extract_inputs(state):
        return {
            "ticker": state["ticker"],
            "current_price": state["current_price"],
            "balance": state["portfolio"]["balance"],
            "holdings": state["portfolio"]["holdings"],
            "risk_profile": state["risk_profile"]["conclusion"],
            "signal_reason": state["llm_decision_reason"],
        }

    stock_count_chain = (
        extract_inputs
        | stock_count_prompt
        | llm
        | (lambda x: x.content)  # Just extract JSON string
    )

    return RunnableLambda(lambda state: {
        **state,
        "stock_count_decision": stock_count_chain.invoke(state)
    })
