# volatility_indicators.py
"""
Volatility-based technical indicators using ta library.
"""
import pandas as pd
from ta import volatility

def calculate_bollinger_bands(close: pd.Series, window: int = 20, window_dev: int = 2) -> pd.DataFrame:
    """Purpose: Detect price breakouts and volatility contractions/expansions"""
    bb = volatility.BollingerBands(close=close, window=window, window_dev=window_dev)
    return pd.DataFrame({
        'bb_upper': bb.bollinger_hband(),
        'bb_lower': bb.bollinger_lband(),
        'bb_width': bb.bollinger_wband()
    })

def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Purpose: Gauge market volatility for risk-based sizing and stop loss"""
    return volatility.AverageTrueRange(
        high=high,
        low=low,
        close=close,
        window=window
    ).average_true_range()

