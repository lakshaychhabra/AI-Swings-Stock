# volume_indicators.py
"""
Volume-based technical indicators using ta library.
"""
import pandas as pd
from ta import volume

def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume_series: pd.Series) -> pd.Series:
    """Purpose: Identify fair intraday average price level weighted by volume"""
    return volume.VolumeWeightedAveragePrice(
        high=high,
        low=low,
        close=close,
        volume=volume_series
    ).volume_weighted_average_price()

def calculate_obv(close: pd.Series, volume_series: pd.Series) -> pd.Series:
    """Purpose: Confirm trend strength based on volume movements"""
    return volume.OnBalanceVolumeIndicator(
        close=close,
        volume=volume_series
    ).on_balance_volume()