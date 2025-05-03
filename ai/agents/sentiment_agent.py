from langgraph.graph import StateGraph, END
from core.websearch.search_web import search_with_brave, scrape_articles
from langchain.prompts import ChatPromptTemplate
from ai.llm.gemini import llm
import json, os
from datetime import date
from langchain_core.runnables import RunnableLambda

prompt = ChatPromptTemplate.from_template("""
    You're a trading assistant. Given the market news, output your decision in **valid JSON**.

    Respond ONLY in the following format:

    ```json
    {{
    "decision": "Buy" | "Sell" | "Hold",
    "reason": "<detailed structured explanation>"
    }}
    ```
                                          
    here is the news scraped from the web:
    {news}
""")

def llm_decision(state):
    success = False
    if state.get("news"):
        messages = prompt.format_prompt(
            news=state["news"]).to_messages()
        result = llm.invoke(messages)
        success = True
    else:
        result = {"success": False, "decision": "Hold", "reason": "No news found"}

    return {
        **state,
        "decision": result.decision,
        "reason": result.reason,
        "success": success,
    }


def create_graph(include_scraper=True):
    builder = StateGraph(dict)
    
    builder.add_node("search", search_with_brave)
    builder.add_node("decide", RunnableLambda(llm_decision))

    if include_scraper:
        builder.add_node("scrape", scrape_articles)
        builder.set_entry_point("search")
        builder.add_edge("search", "scrape")
        builder.add_edge("scrape", "decide")
        builder.add_edge("decide", END)
    else:
        builder.set_entry_point("search")
        builder.add_edge("search", END)

    return builder.compile()

news_agent = create_graph()
