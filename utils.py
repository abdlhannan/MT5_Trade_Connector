"""
Utility functions for MetaTrader 5 data handling.
"""
from MetaTrader5 import (
    initialize,
    copy_rates_from_pos,
    TIMEFRAME_M1,
    TIMEFRAME_M5,
    TIMEFRAME_M15,
    TIMEFRAME_M30,
    TIMEFRAME_H1,
    TIMEFRAME_H4,
    TIMEFRAME_D1,
)
import pandas as pd
import numpy as np


# Mapping of timeframe strings to MT5 constants
TIMEFRAME_MAP = {
    'M1': TIMEFRAME_M1,
    'M5': TIMEFRAME_M5,
    'M15': TIMEFRAME_M15,
    'M30': TIMEFRAME_M30,
    'H1': TIMEFRAME_H1,
    'H4': TIMEFRAME_H4,
    'D1': TIMEFRAME_D1,
}


def return_df(rates_array):
    """
    Convert MT5 rates array to pandas DataFrame.
    
    Args:
        rates_array: Array of rates from MT5 containing OHLCV data
        
    Returns:
        pandas.DataFrame: DataFrame with columns for date_time, OHLC, volume, and spread data
    """
    date_time = [x[0] for x in rates_array]
    open_price = [x[1] for x in rates_array]
    high = [x[2] for x in rates_array]
    low = [x[3] for x in rates_array]
    close = [x[4] for x in rates_array]
    tick_volume = [x[5] for x in rates_array]
    spread = [x[6] for x in rates_array]
    real_volume = [x[7] for x in rates_array]
    
    date_time = pd.to_datetime(date_time, unit='s')
    df = pd.DataFrame(
        np.transpose(np.array([date_time, open_price, high, low, close, tick_volume, spread, real_volume])),
        columns=['date_time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']
    )
    return df


def MT5_DATAGENERATOR_v2(pair, time_frame, win):
    """
    Generate historical price data from MT5 for a given pair and timeframe.
    
    Args:
        pair: Trading pair symbol (e.g., 'EURUSD')
        time_frame: Timeframe string ('M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1')
        win: Number of bars to retrieve
        
    Returns:
        pandas.DataFrame: DataFrame containing OHLCV data
        
    Raises:
        ValueError: If timeframe is not supported
    """
    initialize()
    
    if time_frame not in TIMEFRAME_MAP:
        raise ValueError(f'Unsupported timeframe: {time_frame}. Supported timeframes: {list(TIMEFRAME_MAP.keys())}')
    
    rates_array = copy_rates_from_pos(pair, TIMEFRAME_MAP[time_frame], 0, win)
    return return_df(rates_array)