import numpy as np
import math
from math import nan

def floatify_indicators(indicators: dict) -> dict:
    """Convert all numeric values to native Python float/int, replace NaNs with None."""
    cleaned = {}
    for k, v in indicators.items():
        if isinstance(v, (np.generic, float, int)):
            val = float(v)
            cleaned[k] = None if math.isnan(val) or math.isinf(val) else val
        else:
            cleaned[k] = v
    return cleaned

def clean_ta(ta_decision: dict) -> dict:
    """Clean TA decision for JSON compatibility: remove candles, clean indicators."""
    ta_cleaned = dict(ta_decision)  # shallow copy
    ta_cleaned.pop("candles", None)

    if "indicators" in ta_cleaned:
        for tf in ["15m", "60m"]:
            if tf in ta_cleaned["indicators"]:
                ta_cleaned["indicators"][tf] = floatify_indicators(ta_cleaned["indicators"][tf])

    return ta_cleaned

import json
from datetime import datetime
from pathlib import Path

def safe_default(o):
    if isinstance(o, Exception):
        return {"error": str(o), "type": o.__class__.__name__}
    if isinstance(o, datetime):
        return o.isoformat()
    if isinstance(o, Path):
        return str(o)
    if hasattr(o, "__dict__"):
        return o.__dict__
    return f"<<non-serializable: {o.__class__.__name__}>>"

def safe_json(data, pretty=False):
    return json.dumps(
        data,
        indent=2 if pretty else None,
        default=safe_default
    )
