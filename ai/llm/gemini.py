from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

class TradeDecision(BaseModel):
    decision: str  # "Buy" | "Sell" | "Hold"
    reason: str

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25", temperature=0.0001).with_structured_output(TradeDecision)

class BuyCountDecision(BaseModel):
    decision: str  # "Buy" | "Sell" | "Hold"
    reason: str
    quantity: int
    expected_profit: float
    stop_loss: float
    target: float

llm_stock_count = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25", temperature=0.0001).with_structured_output(BuyCountDecision)