from langchain.prompts import ChatPromptTemplate
from llm.gemini import llm

    
combine_prompt = ChatPromptTemplate.from_template("""
You are a Swing Trader in Wallstreet. Given the following signals from Multiple Source agents:

- News Agent Decision: {news_decision}
- News Reason: {news_reason}

- TA Agent Decision: {ta_decision}
- TA Reason: {ta_reason}

- Risk Agent Decision: {risk_decision}
- Risk Reason: {risk_reason}

Respond in **valid JSON**:

```json
{{
  "decision": "Buy" | "Sell" | "Hold",
  "reason": "<your combined analysis>"
}}
""")

def combine_signals(news, ta, risk):
    messages = combine_prompt.format_prompt(
        news_decision=news["decision"],
        news_reason=news["reason"],
        ta_decision=ta["decision"],
        ta_reason=ta["reason"],
        risk_decision=risk["decision"],
        risk_reason=risk["reason"]
    ).to_messages()

    result = llm.invoke(messages)

    return {
    "final_decision": result.decision,
    "final_reason": result.reason
    }   
