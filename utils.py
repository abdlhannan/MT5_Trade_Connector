from MetaTrader5 import *
import pandas as pd
import numpy as np
def MT5_DATAGENERATOR_v2(pair, time_frame, win):

    initialize()
    if 'M1' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_M1, 0, win)
        return return_df(rates_array)
    if 'M5' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_M5, 0, win)
        return return_df(rates_array)
    if 'M15' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_M15, 0, win)
        return return_df(rates_array)
    if 'M30' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_M30, 0, win)
        return return_df(rates_array)
    if 'H1' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_H1, 0, win)
        return return_df(rates_array)
    if 'H4' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_H4, 0, win)
        return return_df(rates_array)
    if 'D1' == time_frame:
        rates_array = copy_rates_from_pos(pair, TIMEFRAME_D1, 0, win)
        return return_df(rates_array)
    raise Exception('Error in getting data')
    #return None
def return_df(rates_array):
    date_time = [x[0] for x in rates_array]
    open = [x[1] for x in rates_array]
    high = [x[2] for x in rates_array]
    low = [x[3] for x in rates_array]
    close = [x[4] for x in rates_array]
    tick_volume = [x[5] for x in rates_array]
    spread = [x[6] for x in rates_array]
    real_volume = [x[7] for x in rates_array]
    date_time = pd.to_datetime(date_time, unit='s')
    df = pd.DataFrame(np.transpose(np.array([date_time, open, high, low, close, tick_volume, spread, real_volume])),
                    columns = ['date_time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume'])
    return df