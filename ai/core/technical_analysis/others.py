
import pandas as pd

def calculate_mass_index(high: pd.Series, low: pd.Series, window: int = 25) -> pd.Series:
    """
    Purpose: Detect potential trend reversals based on range expansion and contraction.
    """
    high_low_range = high - low
    single_ema = high_low_range.ewm(span=9, adjust=False).mean()
    double_ema = single_ema.ewm(span=9, adjust=False).mean()
    mass = single_ema / double_ema
    mass_index = mass.rolling(window=window).sum()
    return mass_index


def calculate_ulcer_index(close: pd.Series, window: int = 14) -> pd.Series:
    """
    Purpose: Measure depth and duration of drawdowns for risk assessment in prolonged holds.
    """
    rolling_max = close.rolling(window=window, min_periods=1).max()
    drawdown = ((close - rolling_max) / rolling_max) * 100
    squared_drawdown = drawdown ** 2
    ulcer_index = (squared_drawdown.rolling(window=window, min_periods=1).mean()) ** 0.5
    return ulcer_index


def calculate_kama(close: pd.Series, window: int = 10, fastend: float = 2/ (2 + 1), slowend: float = 2/ (30 + 1)) -> pd.Series:
    """
    Purpose: Smoothen price movements adaptively, responding faster during volatility, slower during trends.
    """
    # Efficiency Ratio (ER)
    change = close.diff(window).abs()
    volatility = close.diff().abs().rolling(window=window).sum()
    er = change / volatility

    # Smoothing Constant (SC)
    sc = (er * (fastend - slowend) + slowend) ** 2

    # Initialize KAMA
    kama = close.copy()
    for i in range(window, len(close)):
        kama.iat[i] = kama.iat[i-1] + sc.iat[i] * (close.iat[i] - kama.iat[i-1])

    return kama