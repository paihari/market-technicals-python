#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from datetime import datetime

from binance.client import Client
from binance.enums import *
from binance.helpers import round_step_size

from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError

from datetime import datetime
from pprint import pformat
from binance.helpers import round_step_size

import numpy as np
import pandas as pd
import json
import time
import math

import schedule
import sys
import socket


# In[ ]:


global client;


# In[ ]:


global target_ticker_list


# In[ ]:


def init():
    global client
    client = Client('', '', {"verify": True, "timeout": 20})
    cmc = CoinMarketCapAPI('')
    info_all_tickers  = client.get_all_tickers()
    quote_ccy = 'USDT'
    ticker_list = [d['symbol'] for d in info_all_tickers if d['symbol'].endswith(quote_ccy)]
    rank_info = cmc.cryptocurrency_map(sort='cmc_rank').data
    target_rank_info = [d['symbol']+quote_ccy for d in rank_info if d['rank'] >= 1 and d['rank'] <= 300]
    global target_ticker_list
    rank_filtered_ticker_list = [d for d in ticker_list if d in target_rank_info]
    # target_ticker_list = ['RIFUSDT']
    pair_details = client.get_all_isolated_margin_symbols()
    margin_pair_list = [d['symbol'] for d in pair_details if d['quote'] == quote_ccy and d['isMarginTrade'] == True]   
    target_ticker_list = [d for d in rank_filtered_ticker_list if d in margin_pair_list]
    return target_ticker_list
    


# In[ ]:


def is_candidate(filtered_klines_info): 
    is_candidate = False
    
    buy_kline_info = filtered_klines_info[0]
    buy_kline_average_volume = buy_kline_info[5]

    
    strong_context_kline_info = filtered_klines_info[1:len(filtered_klines_info)]


    
    strong_context_kline_average_volume = np.mean(strong_context_kline_info[:,5])
    
    for strong_context_kline in strong_context_kline_info:
        perc_change = strong_context_kline[-1]
        perc_volume = strong_context_kline[5] / buy_kline_average_volume

        if perc_change > 1 or perc_change < -5  or perc_volume > 0.7:
            return False
        
    buy_line_open_price = buy_kline_info[1]
    buy_line_high_price = buy_kline_info[2]
    buy_line_low_price = buy_kline_info[3]
    buy_line_close_price = buy_kline_info[4]

    #Drop from high price to close price should be in the range of 10 - 15%
    drop_from_high_to_close_gate =   1.20 > buy_line_high_price/buy_line_close_price > 1.05


    #Percentage increase should be in the range of 7 - 15%
    percentage_gate = 1.5 > buy_kline_info[-1] > 1

    if percentage_gate and True and True:

        is_candidate = True
    else:
        is_candidate = False

    return is_candidate


# In[ ]:


def find_percentage_increase_or_decrease(focused_kline_array):
    percentage_value = []
    for kline in focused_kline_array:
        diff = kline[4] - kline[1]
        perc_diff = diff/kline[1]
        percentage_value.append(perc_diff*100)
    return percentage_value 


# In[ ]:


def adjust_price(target_ticker, price):
    info = client.get_symbol_info(target_ticker)
    tick_size = info['filters'][0]['tickSize']
    adjusted_price = round_step_size(price, tick_size)
    adjusted_price = np.format_float_positional(adjusted_price, trim='-')
    return adjusted_price
    


# In[ ]:


def trade_candidate(target_ticker, buy_kline_info) :
    
    usdt = 1000
    order = client.create_order(symbol=target_ticker, side=SIDE_BUY, type='MARKET', quoteOrderQty=usdt)
    
    time.sleep(1)
    order_id = order['orderId'] 
    while client.get_order(symbol=target_ticker, orderId=order_id)['status'] != 'FILLED':
        time.sleep(1)
        
    buy_price = order['fills'][0]['price']
    buy_qty = order['executedQty']
    sell_price = float(buy_price) * 1.1
    
    adjusted_sell_price = str(adjust_price(target_ticker, sell_price))
    
    print('Order ID')
    print(order_id)
    print('Buy Price')
    print(buy_price)
    print('Buy Qty')
    print(buy_qty)
    print('Sell Price')
    print(adjusted_sell_price)
    
    if client.get_order(symbol=target_ticker, orderId=order_id)['status'] == 'FILLED':
        asset = target_ticker.split("USDT")[0]
        balance = client.get_asset_balance(asset=asset)
        free_to_trade = balance['free']

        order = client.create_order(symbol=target_ticker, side=SIDE_SELL, type='LIMIT', quantity=float(buy_qty), price=adjusted_sell_price, timeInForce=TIME_IN_FORCE_GTC)
        print('********** SELL ORDER SET ************************')

    


# In[ ]:


def trade_tickers():
    try: 
        
        for target_ticker in target_ticker_list:

            client = Client('', '')
            klines = client.get_historical_klines(target_ticker, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC") 
            length = int(len(klines))
            if(length < 24):
                continue
            
            klines.pop()

            array = np.array(klines, dtype=np.float64)
            focused_kline_array = np.delete(array, [6, 7, 8, 9, 10, 11], 1)
            percentage_value = find_percentage_increase_or_decrease(focused_kline_array)
            percentage_value = np.reshape(percentage_value, (length -1 , 1))
            focused_kline_array = np.append(focused_kline_array, percentage_value, 1)

            focused_reverse_kline_array = focused_kline_array[::-1]
            
            filtered_klines_info = focused_reverse_kline_array[0:6]
            if(len(filtered_klines_info) == 6):
                if(is_candidate(filtered_klines_info)):
                    print('*************** TRADE ****************')
                    print(target_ticker)
                    buy_kline_info = filtered_klines_info[0]
                    trade_candidate(target_ticker, buy_kline_info)
                    client.close_connection
                
    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)


# In[ ]:


def liquidate_tickers():
    try: 
        client = Client('', '')
        open_orders = client.get_open_orders()
        for open_order in open_orders:
            order_time = open_order['time']
            symbol = open_order['symbol']
            quantity = open_order['origQty']
            orderId = open_order['orderId']
            now_time_stamp = math.floor(time.time() * 1000)
            diff_in_time_now_to_buy_time = now_time_stamp - order_time

            if diff_in_time_now_to_buy_time > 9600000:
                print('************** LIQUIDATE ***********')
                print(symbol)
                client.cancel_order(symbol=symbol, orderId=orderId)
                time.sleep(2)
                client.order_market_sell(symbol=symbol,quantity=quantity)
        client.close_connection
    
    except BinanceAPIException as e:
        print(e.status_code)
        print(e.message)


# In[ ]:


def job():
    
    
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("Start Date and time =", dt_string)
    
    init()
    
    print('Job Run Trade Tickers')
    trade_tickers()
    
    print('Job Run Liquidate Tickers')
    liquidate_tickers()
    
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("End Date and time =", dt_string)
    


# In[ ]:


schedule.every().hour.at(":01").do(job)


# In[ ]:


while True:
    schedule.run_pending()
    time.sleep(1)

