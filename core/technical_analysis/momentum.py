"""
Momentum-based technical indicators using ta library.
"""
import pandas as pd
from ta import momentum, trend

def calculate_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Purpose: Detect overbought/oversold conditions quickly"""
    return momentum.RSIIndicator(close=close, window=window).rsi()

def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                        window: int = 14, smooth_window: int = 3) -> pd.DataFrame:
    """Purpose: Identify quick reversal points"""
    stoch = momentum.StochasticOscillator(
        high=high,
        low=low,
        close=close,
        window=window,
        smooth_window=smooth_window
    )
    return pd.DataFrame({
        'stoch_k': stoch.stoch(),
        'stoch_d': stoch.stoch_signal()
    })

def calculate_macd(close: pd.Series, window_slow: int = 26, 
                  window_fast: int = 12, window_sign: int = 9) -> pd.DataFrame:
    """Purpose: Catch trend reversals with fast-slow signal crossovers"""
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

def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, 
                        window: int = 14) -> pd.Series:
    """Purpose: Identify overbought/oversold zones using Williams %R"""
    return momentum.WilliamsRIndicator(
        high=high,
        low=low,
        close=close,
        lbp=window
    ).williams_r()

def calculate_awesome_oscillator(high: pd.Series, low: pd.Series,
                               window1: int = 5, window2: int = 34) -> pd.Series:
    """Purpose: Capture momentum shifts faster than MACD"""
    return momentum.AwesomeOscillatorIndicator(
        high=high,
        low=low,
        window1=window1,
        window2=window2
    ).awesome_oscillator()

def calculate_roc(close: pd.Series, window: int = 12) -> pd.Series:
    """Purpose: Detect rapid price movements and trend continuation"""
    return momentum.ROCIndicator(
        close=close,
        window=window
    ).roc()