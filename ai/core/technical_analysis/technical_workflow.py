# workflow_runner.py
"""
Strict workflow to run all technical analysis functions listed in README.
"""

import pandas as pd
from core.technical_analysis.momentum import (
    calculate_rsi,
    calculate_stochastic,
    calculate_macd,
    calculate_williams_r,
    calculate_awesome_oscillator,
    calculate_roc
)
from core.technical_analysis.trend import (
    calculate_ema,
    calculate_macd_trend,
    calculate_ichimoku
)
from core.technical_analysis.volatility import (
    calculate_bollinger_bands,
    calculate_atr
)
from core.technical_analysis.volume import (
    calculate_vwap,
    calculate_obv
)
from core.technical_analysis.others import (
    calculate_mass_index,
    calculate_ulcer_index,
    calculate_kama
)

def run_technical_analysis(candle_df: pd.DataFrame, latest_volume=None, avg_volume_30d=None) -> dict:
    """
    Takes in a rolling candle DataFrame (5min, 15min, or 1hr).
    Returns a dictionary with indicators defined in README + extra risk-related features.
    """
    output = {}

    # Momentum
    output['rsi'] = calculate_rsi(candle_df['close']).iloc[-1]

    stoch = calculate_stochastic(candle_df['high'], candle_df['low'], candle_df['close'])
    output['stoch_k'] = stoch['stoch_k'].iloc[-1]
    output['stoch_d'] = stoch['stoch_d'].iloc[-1]

    macd = calculate_macd(candle_df['close'])
    output['macd'] = macd['macd'].iloc[-1]
    output['macd_signal'] = macd['macd_signal'].iloc[-1]
    output['macd_hist'] = macd['macd_hist'].iloc[-1]
    output['macd_crossover'] = int(
        macd['macd'].iloc[-1] > macd['macd_signal'].iloc[-1] and
        macd['macd'].iloc[-2] <= macd['macd_signal'].iloc[-2]
    )

    output['williams_r'] = calculate_williams_r(candle_df['high'], candle_df['low'], candle_df['close']).iloc[-1]
    output['awesome_oscillator'] = calculate_awesome_oscillator(candle_df['high'], candle_df['low']).iloc[-1]
    output['roc'] = calculate_roc(candle_df['close']).iloc[-1]

    # Trend
    output['ema_9'] = calculate_ema(candle_df['close'], window=9).iloc[-1]

    macd_trend = calculate_macd_trend(candle_df['close'])
    output['macd_trend'] = macd_trend['macd'].iloc[-1]
    output['macd_trend_signal'] = macd_trend['macd_signal'].iloc[-1]
    output['macd_trend_hist'] = macd_trend['macd_hist'].iloc[-1]

    ichimoku = calculate_ichimoku(candle_df['high'], candle_df['low'])
    output['tenkan_sen'] = ichimoku['tenkan_sen'].iloc[-1]
    output['kijun_sen'] = ichimoku['kijun_sen'].iloc[-1]
    output['ichimoku_cross'] = int(
        ichimoku['tenkan_sen'].iloc[-1] > ichimoku['kijun_sen'].iloc[-1]
    )

    # Volatility
    bb = calculate_bollinger_bands(candle_df['close'])
    output['bb_upper'] = bb['bb_upper'].iloc[-1]
    output['bb_lower'] = bb['bb_lower'].iloc[-1]
    output['bb_width'] = bb['bb_width'].iloc[-1]

    output['atr'] = calculate_atr(candle_df['high'], candle_df['low'], candle_df['close']).iloc[-1]
    output['atr_norm'] = output['atr'] / candle_df['close'].iloc[-1]

    # Volume
    output['vwap'] = calculate_vwap(candle_df['high'], candle_df['low'], candle_df['close'], candle_df['volume']).iloc[-1]
    output['obv'] = calculate_obv(candle_df['close'], candle_df['volume']).iloc[-1]

    if latest_volume is not None and avg_volume_30d is not None:
        output['volume_spike'] = latest_volume / max(avg_volume_30d, 1)

    # Others (Risk/Adaptive)
    output['mass_index'] = calculate_mass_index(candle_df['high'], candle_df['low']).iloc[-1]
    output['ulcer_index'] = calculate_ulcer_index(candle_df['close']).iloc[-1]
    output['kama'] = calculate_kama(candle_df['close']).iloc[-1]

    return output


def run_technical_analysis_old(candle_df: pd.DataFrame) -> dict:
    """
    Takes in a rolling candle DataFrame (5min, 15min, or 1hr).
    Returns a dictionary with ONLY the indicators defined in README.
    """
    output = {}

    # Momentum
    output['rsi'] = calculate_rsi(candle_df['close']).iloc[-1]

    stoch = calculate_stochastic(candle_df['high'], candle_df['low'], candle_df['close'])
    output['stoch_k'] = stoch['stoch_k'].iloc[-1]
    output['stoch_d'] = stoch['stoch_d'].iloc[-1]

    # macd = calculate_macd(candle_df['close'])
    # output['macd'] = macd['macd'].iloc[-1]
    # output['macd_signal'] = macd['macd_signal'].iloc[-1]
    # output['macd_hist'] = macd['macd_hist'].iloc[-1]

    output['williams_r'] = calculate_williams_r(candle_df['high'], candle_df['low'], candle_df['close']).iloc[-1]
    output['awesome_oscillator'] = calculate_awesome_oscillator(candle_df['high'], candle_df['low']).iloc[-1]
    output['roc'] = calculate_roc(candle_df['close']).iloc[-1]

    # Trend
    output['ema_9'] = calculate_ema(candle_df['close'], window=9).iloc[-1]

    macd_trend = calculate_macd_trend(candle_df['close'])
    output['macd_trend'] = macd_trend['macd'].iloc[-1]
    output['macd_trend_signal'] = macd_trend['macd_signal'].iloc[-1]
    output['macd_trend_hist'] = macd_trend['macd_hist'].iloc[-1]

    ichimoku = calculate_ichimoku(candle_df['high'], candle_df['low'])
    output['tenkan_sen'] = ichimoku['tenkan_sen'].iloc[-1]
    output['kijun_sen'] = ichimoku['kijun_sen'].iloc[-1]

    # Volatility
    bb = calculate_bollinger_bands(candle_df['close'])
    output['bb_upper'] = bb['bb_upper'].iloc[-1]
    output['bb_lower'] = bb['bb_lower'].iloc[-1]
    output['bb_width'] = bb['bb_width'].iloc[-1]

    output['atr'] = calculate_atr(candle_df['high'], candle_df['low'], candle_df['close']).iloc[-1]

    # Volume
    output['vwap'] = calculate_vwap(candle_df['high'], candle_df['low'], candle_df['close'], candle_df['volume']).iloc[-1]
    output['obv'] = calculate_obv(candle_df['close'], candle_df['volume']).iloc[-1]

    # Others (Risk/Adaptive)
    output['mass_index'] = calculate_mass_index(candle_df['high'], candle_df['low']).iloc[-1]
    output['ulcer_index'] = calculate_ulcer_index(candle_df['close']).iloc[-1]
    output['kama'] = calculate_kama(candle_df['close']).iloc[-1]

    return output

# # Example usage
# if __name__ == "__main__":
#     # Simulated DataFrame example
#     df = pd.read_csv("your_sample_data.csv")  # Must have open, high, low, close, volume columns
#     signals = run_technical_analysis(df)
#     print(signals)
