from newspaper import Article
from config.env import BRAVE_API_KEY
import json
from langchain_community.tools.brave_search.tool import BraveSearch

brave = BraveSearch(api_key=BRAVE_API_KEY)
def search_with_brave(state):   
    result = brave.run(state["topic"])

    try:
        results = json.loads(result)
        urls = [item["link"] for item in results][:4]
    except Exception as e:
        urls = []
    
    return {
        "topic": state["topic"],
        "urls": urls,
        "search_results": results if 'results' in locals() else [],
    }

def extract_urls(state):
    data = json.loads(state["search_results"])
    urls = [item["link"] for item in data][:7]
    return {"urls": urls}


def scrape_articles(state, config):
    articles = []
    for url in state["urls"]:
        try:
            article = Article(url)
            article.download()
            article.parse()
            articles.append({
                "title": article.title,
                "url": url,
                "publish_date": str(article.publish_date) if article.publish_date else None,
                "content": article.text[:3000]
            })
        except Exception as e:
            articles.append({"url": url, "error": str(e)})
    return {"news": articles}

# def scrape_articles(state, config):
#     return {
#         "topic": state["topic"],
#         "articles": [
#             {
#                 "url": url,
#                 "title": "Dummy title",
#                 "publish_date": None,
#                 "content": f"Placeholder content for {url}"
#             } for url in state.get("urls", [])
#         ]
#     }