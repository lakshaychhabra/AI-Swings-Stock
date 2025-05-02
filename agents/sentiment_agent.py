from langgraph.graph import StateGraph, END
from websearch.search_web import search_with_brave, scrape_articles
from langchain.prompts import ChatPromptTemplate
from llm.llm import llm
import json, os
from datetime import date

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
    messages = prompt.format_prompt(
        ticker=state["news"]).to_messages()
    
    result = llm.invoke(messages)

    return {
        **state,
        "decision": result.decision,
        "reason": result.reason,
    }


def create_graph(include_scraper=True):
    builder = StateGraph(dict)
    
    builder.add_node("search", search_with_brave)

    if include_scraper:
        builder.add_node("scrape", scrape_articles)
        builder.set_entry_point("search")
        builder.add_edge("search", "scrape")
        builder.add_edge("scrape", END)
    else:
        builder.set_entry_point("search")
        builder.add_edge("search", END)

    return builder.compile()

news_agent = create_graph()

NEWS_CACHE = "data/news_cache.json"

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
        state = news_agent.invoke({"topic": f"{ticker} stock trends"})
        news_result = {
            "date": today,
            "news": state["articles"],
            "decision": state["decision"],
            "reason": state["reason"]
        }
        data[ticker] = news_result

        with open(NEWS_CACHE, "w") as f:
            json.dump(data, f, indent=2)

        return news_result