import pandas as pd
from ta import trend

def calculate_ema(close: pd.Series, window: int = 9) -> pd.Series:
    """Purpose: Smooth out short-term price fluctuations"""
    return trend.EMAIndicator(close=close, window=window).ema_indicator()

def calculate_macd_trend(close: pd.Series, window_slow: int = 26,
                        window_fast: int = 12, window_sign: int = 9) -> pd.DataFrame:
    """Purpose: Identify trend direction and momentum"""
    macd_ind = trend.MACD(
        close=close,
        window_slow=window_slow,
        window_fast=window_fast,
        window_sign=window_sign
    )
    return pd.DataFrame({
        'macd': macd_ind.macd(),
        'macd_signal': macd_ind.macd_signal(),
        'macd_hist': macd_ind.macd_diff()
    })

def calculate_psar(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """Purpose: Spot trend reversals and set trailing stop-losses"""
    return trend.PSARIndicator(high=high, low=low, close=close).psar()

def calculate_ichimoku(high: pd.Series, low: pd.Series) -> pd.DataFrame:
    """Purpose: Provide dynamic support/resistance and trend signals"""
    ichi = trend.IchimokuIndicator(high=high, low=low)
    return pd.DataFrame({
        'tenkan_sen': ichi.ichimoku_conversion_line(),
        'kijun_sen': ichi.ichimoku_base_line()
    })