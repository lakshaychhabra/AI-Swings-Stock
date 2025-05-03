import json
import os

STATE_DIR = "states"
os.makedirs(STATE_DIR, exist_ok=True)

def load_state(ticker: str):
    path = os.path.join(STATE_DIR, f"{ticker}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"history": []}  # default

def save_state(ticker: str, state: dict):
    path = os.path.join(STATE_DIR, f"{ticker}.json")
    with open(path, "w") as f:
        json.dump(state, f, indent=2)
