from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

class TradeDecision(BaseModel):
    decision: str  # "Buy" | "Sell" | "Hold"
    reason: str

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25", temperature=0.001).with_structured_output(TradeDecision)
