import time
import MetaTrader5 as mt5
from utils import *
import threading
import datetime
import numpy as np
import schedule
import schedule as sched2
from threading import Timer
class Periodic_Timer_Thread(object):
    def __init__(self, interval, function, comment='', *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.comment = comment
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.setName(self.comment)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class RiskManagement_v1(object):
    def login(self):
        # display data on the MetaTrader 5 package
        print("MetaTrader5 package author: ", mt5.__author__)
        print("MetaTrader5 package version: ", mt5.__version__)
        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize(self.PATH):
            print("initialize() failed, error code =",mt5.last_error())
            quit()

        authorized = mt5.login(self.login_id, password=self.password)
        if not authorized:
            print('LOGIN FAILED!!!')
            mt5.shutdown()
            quit()
        else:
            print("Login with account: ",str(self.login_id), " successfull!!!")
    def __init__(self,
                login,
                password,
                PATH,
                daily_limit=0.05,
                monthly_limit=0.10):
        self.login_id = login
        self.password = password
        self.PATH = PATH
        self.login()
    def daily_losslimit_check(self):
        from_date = datetime.datetime(2020, 5, 27)
        to_date = datetime.datetime(2020, 5, 29)
        position_history_orders = mt5.history_orders_get(from_date, to_date)
        #print(history_orders)
        df=pd.DataFrame(list(position_history_orders),columns=position_history_orders[0]._asdict().keys())
        #df.drop(['time_expiration','type_time','state','position_by_id','reason','volume_current','price_stoplimit','sl','tp'], axis=1, inplace=True)
        df['time_setup'] = pd.to_datetime(df['time_setup'], unit='s')
        df['time_done'] = pd.to_datetime(df['time_done'], unit='s')
        print(df[['time_done', 'time_setup', 'symbol']])

class MT5_TRADECONNECTOR(object):
    def login(self):
        # display data on the MetaTrader 5 package
        #print("MetaTrader5 package author: ", mt5.__author__)
        #print("MetaTrader5 package version: ", mt5.__version__)
        # establish connection to the MetaTrader 5 terminal
        if not mt5.initialize(self.PATH):
            print("initialize() failed, error code =",mt5.last_error())
            quit()

        authorized = mt5.login(self.login_id, password=self.password)
        if not authorized:
            print('LOGIN FAILED!!!')
            mt5.shutdown()
            quit()
        else:
            print("Login with account: ",str(self.login_id), " successfull!")

    def __init__(self,
                login,
                password,
                strategy_name,
                TimeFrame,
                maxposition,
                PATH="", TrailingStopOn=False):
        '''
        IMPORTANT NOTICE:
        Strategy_name should be max three words.
        Timeframe should be in the following format: M1, M15, M30, H1, H4, D1
        
        '''
        self.strategy_name = strategy_name
        self.TimeFrame = TimeFrame
        self.login_id = login
        self.password = password
        self.PATH = PATH
        #self.login()
        #self.result = None
        self.threads = []
        self.TrailingStopOn = TrailingStopOn
        self.maxposition = maxposition
        if self.TrailingStopOn == True: 
            container_thread = threading.Thread(target=self.container_thread_routine)
            container_thread.start()

    def container_thread_routine(self):
        now = datetime.datetime.now()
        if self.TimeFrame == 'M1':
            wait_second = 60 - now.second
            interval = 1 * 60
            #print('waiting for ', wait_second, ' seconds')
            time.sleep(wait_second)
        elif self.TimeFrame == 'M15':
            wait_minute = np.ceil(now.minute/15) * 15 - now.minute
            interval = 15 * 60
            wait_second = wait_minute * 60
            #print('waiting for ', wait_second, ' seconds')
            time.sleep(wait_second)
        elif self.TimeFrame == 'M30':
            wait_minute = np.ceil(now.minute/30) * 30 - now.minute
            interval = 30 * 60
            wait_second = wait_minute * 60
            #print('waiting for ', wait_second, ' seconds')
            time.sleep(wait_second)
        else:
            raise Exception('Error in TimeFrame type...Not Supported!!')

        initial_thread = threading.Thread(target=self.change_stoploss)
        self.trailing_stop_thread = Periodic_Timer_Thread(interval = interval, \
                function = self.change_stoploss, comment = 'trailing_stop')
        initial_thread.start()
    def change_stoploss(self):
        #print('starting thread at: ', datetime.datetime.now())
        self.login()
        positions = mt5.positions_get()
        if positions is not None:
            for open_position in positions:
                if open_position.comment.find('TS') != -1:
                    #print('calculating threshold for ', open_position.symbol)
                    self.simplestoploss(open_position)
    def simplestoploss(self, open_position):
        stoploss_limit = np.fromstring(open_position.comment[open_position.comment.find('TS') + 2]\
                + open_position.comment[open_position.comment.find('TS') + 3], dtype=int, sep=' ') 
        takeprofit_limit = np.fromstring(open_position.comment[open_position.comment.find('TP') + 2]\
                + open_position.comment[open_position.comment.find('TP') + 3], dtype=int, sep=' ')
        order_type = open_position.type
        symbol = open_position.symbol
        current_price = open_position.price_current
        point = mt5.symbol_info(symbol).point
        order_timeframe = open_position.comment[open_position.comment.find(self.strategy_name)+3:]
        #print(order_timeframe)
        past_data = MT5_DATAGENERATOR_v2(symbol, order_timeframe, 3)
        #print('current close: ', past_data['close'].iloc[1], ' previous close: ', past_data['close'].iloc[0])
        if order_type == 0: #LONG ORDER
            if (past_data['close'].iloc[1] > past_data['close'].iloc[0]) and open_position.profit > 0:
                
                new_sl = np.double(open_position.price_current - stoploss_limit*10*point)
                print(open_position.symbol+': new sl:', new_sl, ' old SL: ',  open_position.sl)
                if new_sl > open_position.sl:
                    
                    tp = np.double(open_position.price_open + takeprofit_limit*10*point)
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position":open_position.ticket,
                        "symbol": open_position.symbol,
                        "sl": new_sl,
                        "tp": tp,
                        "magic":123456
                        }
                    result = mt5.order_send(request)
                    if self.health_check(result._asdict()) == 'pass':
                        print(open_position.symbol, ' SL Changed!!! Strategy: ', self.strategy_name, ' on TIMEFRAME: ', self.TimeFrame)
                    #if result['retcode'] != mt5.TRADE_RETCODE_DONE:
                    #    print("2. order_send failed, retcode={}".format(result['retcode']))
        elif order_type == 1: #SHORT ORDER
            if (past_data['close'].iloc[1] < past_data['close'].iloc[0]) and open_position.profit > 0:
                #print('change detected in ', open_position.symbol)
                new_sl = np.double(open_position.price_current + stoploss_limit*10*point)
                print(open_position.symbol+': new sl:', new_sl, ' old SL: ',  open_position.sl)
                if new_sl < open_position.sl:
                    tp = np.double(open_position.price_open - takeprofit_limit*10*point)
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position":open_position.ticket,
                        "symbol": open_position.symbol,
                        "sl": new_sl,
                        "tp": tp,
                        "magic":123456
                        }
                    result = mt5.order_send(request)
                    if self.health_check(result._asdict()) == 'pass':
                        print(open_position.symbol, ' SL Changed!!! Strategy: ', self.strategy_name, ' on TIMEFRAME: ', self.TimeFrame)
                        #print(result)
        else:
            raise Exception('Error in order_type') 

    def avoid_multiple_positions(self, POSITION, PAIR):
        #THIS FUNCTION RESTRICTS THE BOT TO ONLY HAVE OPEN MAXPOSITION OF THE SAME INSTRUMENT PER STRATEGY
        #ALSO IT CLOSES AN EXISTING POSITION IF STRATEGY GIVES OPPOSITE OF ONGOING OPEN POSITION
        if POSITION == 'LONG':
            position_type = 0
        elif POSITION == 'SHORT':
            position_type = 1
        self.login()
        positions = mt5.positions_get()
        position_count = 0
        for open_position in positions:
            if open_position.comment.find(self.strategy_name) != -1 and open_position.comment.find(self.TimeFrame) != -1:
                if open_position.symbol == PAIR:
                    if (open_position.type == 0 and position_type == 1):
                        #CLOSE A LONG POSITION BY OPPOSITE ORDER
                        request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": open_position.symbol,
                        "volume": open_position.volume,
                        "type": mt5.ORDER_TYPE_SELL,
                        "position": open_position.ticket,
                        "price" : mt5.symbol_info_tick(open_position.symbol).bid,
                        "magic": open_position.magic,
                        "comment": "close long pos",
                        "type_time" : mt5.ORDER_TIME_GTC,
                        "type_filling" : mt5.ORDER_FILLING_FOK,
                        }
                        result = mt5.order_send(request)
                        if self.health_check(self.result._asdict()) == 'pass':
                            print(open_position.symbol, ' with vol: ',open_position.volume,  ' LONG POSITION CLOSED!!! Strategy: ', self.strategy_name, ' on TIMEFRAME: ', self.TimeFrame)
                        #print(result)
                    elif (open_position.type == 1 and position_type == 0):
                        #CLOSE A SHORT POSITION BY OPPOSITE ORDER
                        request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": open_position.symbol,
                        "volume": open_position.volume,
                        "type": mt5.ORDER_TYPE_BUY,
                        "position": open_position.ticket,
                        "price" : mt5.symbol_info_tick(open_position.symbol).ask,
                        "magic": open_position.magic,
                        "comment": "close short pos",
                        "type_time" : mt5.ORDER_TIME_GTC,
                        "type_filling" : mt5.ORDER_FILLING_FOK,
                        }
                        result = mt5.order_send(request)
                        if self.health_check(self.result._asdict()) == 'pass':
                            print(open_position.symbol, ' with vol: ',open_position.volume,  ' SHORT POSITION CLOSED!!! Strategy: ', self.strategy_name, ' on TIMEFRAME: ', self.TimeFrame)
                        #print(result)
                    else:
                        position_count = position_count + 1                
        if position_count >= self.maxposition:
            action = 'block'
        else:
            action = 'noblock'
        return action
    def health_check(self, result):

        if result['retcode'] != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result['retcode']))
            # request the result as a dictionary and display it element by element
            for field in result.keys():
                print("   {}={}".format(field,result[field]))
                # if this is a trading request structure, display it element by element as well
                if field=="request":
                    traderequest_dict=result[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
            return 'notpass'
        else:
            return 'pass'
        
    def marketorder_trade_execution(self, PAIR, lot_size, TP, SL, POSITION):

        """
        mql5 order types
        ENUM_ORDER_TYPE:
            ORDER_TYPE_BUY ; Market Buy order
            ORDER_TYPE_SELL : Market Sell order
            ORDER_TYPE_BUY_LIMIT : Buy Limit pending order
            ORDER_TYPE_SELL_LIMIT : Sell Limit pending order
            ORDER_TYPE_BUY_STOP : Buy Stop pending order
            ORDER_TYPE_SELL_STOP : Sell Stop pending order
            ORDER_TYPE_BUY_STOP_LIMIT : Upon reaching the order price, a pending Buy Limit order is placed at the StopLimit price
            ORDER_TYPE_SELL_STOP_LIMIT : Upon reaching the order price, a pending Sell Limit order is placed at the StopLimit price
            ORDER_TYPE_CLOSE_BY : Order to close a position by an opposite one
        """
        point = mt5.symbol_info(PAIR).point
        if POSITION == 'LONG':
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(PAIR).ask
            sl = np.double(price - SL*10 * point)
            tp = np.double(price + TP*10 * point)
            if self.TrailingStopOn == False:
                comment = 'TP'+str(TP)+' SL'+ str(SL) + ' ' + self.strategy_name+self.TimeFrame 
            else:
                comment = 'TP'+str(TP)+' TS'+ str(SL) + ' ' + self.strategy_name+self.TimeFrame 
            deviation = 5
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": PAIR,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": np.double(sl),
                "tp": np.double(tp),
                "deviation": deviation,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            self.login()
            self.result = mt5.order_send(request) 
            if self.health_check(self.result._asdict()) == 'pass':
                print("1. order_send(): by {} {} lots at {} with deviation={} points".format(PAIR,lot_size,price,deviation));  
        elif POSITION == 'SHORT':
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(PAIR).bid
            sl = np.double(price + SL*10 * point)
            tp = np.double(price - TP*10 * point)
            if self.TrailingStopOn == False:
                comment = 'TP'+str(TP)+' SL'+ str(SL) + ' ' + self.strategy_name+self.TimeFrame 
            else:
                comment = 'TP'+str(TP)+' TS'+ str(SL) + ' ' + self.strategy_name+self.TimeFrame 
            deviation = 5
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": PAIR,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": np.double(sl),
                "tp": np.double(tp),
                "deviation": deviation,
                "magic": 234000,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            self.login()
            self.result = mt5.order_send(request) 
            if self.health_check(self.result._asdict()) == 'pass':
                print("1. order_send(): by {} {} lots at {} with deviation={} points".format(PAIR,lot_size,price,deviation));  
        elif POSITION == 'CLOSE':
            self.login()
            positions = mt5.positions_get()
            if positions is not None:
                for open_position in positions:
                    if open_position.comment.find(self.strategy_name) != -1 and open_position.comment.find(self.TimeFrame) != -1 and PAIR == open_position.symbol:
                        if open_position.order_type == 0:
                            order_type = mt5.ORDER_TYPE_SELL
                            price = mt5.symbol_info_tick(open_position.symbol).bid
                        elif open_position.order_type == 1:
                            order_type = mt5.ORDER_TYPE_BUY
                            price = mt5.symbol_info_tick(open_position.symbol).ask
                        comment = 'closed for ' + self.strategy_name+self.TimeFrame 
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": open_position.symbol,
                            "volume": open_position.volume,
                            "type": order_type,
                            "position": open_position.ticket,
                            "price": price,
                            "deviation": 5,
                            "magic": 0,
                            "comment": comment,
                            "type_time": mt5.ORDER_TIME_GTC, # good till cancelled
                            "type_filling": mt5.ORDER_FILLING_RETURN,
                        }
                        self.login()
                        self.result=mt5.order_send(close_request) 
                        if self.health_check(self.result._asdict()) == 'pass':
                            print("1. order_send(): by {} {} lots at {} with deviation={} points".format(PAIR,lot_size,price,deviation));     
            else:
                return
        else:
            raise('POSITION TYPE IS INVALID FOR MARKET ORDERS!')

        