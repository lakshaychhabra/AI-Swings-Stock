from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from orchestration.pipeline import analyse_ticker

app = FastAPI()

class AnalyseRequest(BaseModel):
    ticker: str

@app.post("/analyse")
def analyse(request: AnalyseRequest):
    result = analyse_ticker(request.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result