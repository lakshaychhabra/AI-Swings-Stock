from langchain.prompts import ChatPromptTemplate
from llm.llm import llm

combine_prompt = ChatPromptTemplate.from_template("""
You are a trading advisor. Given the following signals from two agents:

- News Agent Decision: {news_decision}
- News Reason: {news_reason}

- TA Agent Decision: {ta_decision}
- TA Reason: {ta_reason}

Respond in **valid JSON**:

```json
{{
  "decision": "Buy" | "Sell" | "Hold",
  "reason": "<your combined analysis>"
}}
""")

def combine_signals(news, ta):
    messages = combine_prompt.format_prompt(
        news_decision=news["decision"],
        news_reason=news["reason"],
        ta_decision=ta["decision"],
        ta_reason=ta["reason"] 
    ).to_messages()

    result = llm.invoke(messages)

    return {
    "final_decision": result.decision,
    "final_reason": result.reason
    }   