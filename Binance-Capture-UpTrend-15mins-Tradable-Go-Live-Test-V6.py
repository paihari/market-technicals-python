#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime

from binance.client import Client
from binance.enums import *

from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError

from datetime import datetime
from binance.helpers import round_step_size

import numpy as np
import pandas as pd
import json
import time
import sys


# In[2]:


#client = Client('   ', '  ')


# In[3]:


#cmc = CoinMarketCapAPI('  ')


# In[4]:


#info = client.get_all_tickers()


# In[5]:


#quote_ccy = 'USDT'


# In[6]:


#ticker_list = [d['symbol'] for d in info if d['symbol'].endswith(quote_ccy)]


# In[7]:


#rank_info = cmc.cryptocurrency_map(sort='cmc_rank').data


# In[8]:


#target_rank_info = [d['symbol']+quote_ccy for d in rank_info if d['rank'] >= 100 and d['rank'] <= 500]


# In[9]:


#target_ticker_list = [d for d in ticker_list if d in target_rank_info]


# In[10]:


#target_ticker_list


# In[11]:


#target_ticker_list = ['BONDUSDT']


# In[12]:


global client;


# In[13]:


global target_ticker_list


# In[14]:


def init():
    global client
    client = Client('   ', '  ', {"verify": True, "timeout": 20})
    cmc = CoinMarketCapAPI('  ')
    info_all_tickers  = client.get_all_tickers()
    quote_ccy = 'USDT'
    ticker_list = [d['symbol'] for d in info_all_tickers if d['symbol'].endswith(quote_ccy)]
    rank_info = cmc.cryptocurrency_map(sort='cmc_rank').data
    target_rank_info = [d['symbol']+quote_ccy for d in rank_info if d['rank'] >= 100 and d['rank'] <= 500]
    global target_ticker_list
    target_ticker_list = [d for d in ticker_list if d in target_rank_info]
    # target_ticker_list = ['RIFUSDT']
    return target_ticker_list
    


# In[15]:


def is_candidate(filtered_klines_info): 
    is_candidate = False
    
    buy_kline_info = filtered_klines_info[0]
    buy_kline_average_volume = buy_kline_info[5]

    
    strong_context_kline_info = filtered_klines_info[1:len(filtered_klines_info)]


    
    strong_context_kline_average_volume = np.mean(strong_context_kline_info[:,5])
    
    for strong_context_kline in strong_context_kline_info:
        perc_change = strong_context_kline[-1]
        perc_volume = strong_context_kline[5] / buy_kline_average_volume

        if perc_change > 2 or perc_volume > 0.20:
            return False
        
        buy_line_open_price = buy_kline_info[1]
        buy_line_high_price = buy_kline_info[2]
        buy_line_low_price = buy_kline_info[3]
        buy_line_close_price = buy_kline_info[4]
        
        #Drop from high price to close price should be in the range of 10 - 15%
        drop_from_high_to_close_gate =   1.15 > buy_line_high_price/buy_line_close_price > 1.10
        
        
        #Percentage increase should be in the range of 7 - 15%
        percentage_gate = 12 > buy_kline_info[-1] > 9
        
        #The close price should not have dropped more than 15 % compared to Open Price
        
        mid_price_between_high_and_open_price = (buy_line_open_price + buy_line_high_price) / 2
        
        difference_between_high_and_open_price = buy_line_high_price - buy_line_open_price
        
        permissible_drop_between_open_close_price = (difference_between_high_and_open_price * 85) / 100
        drop_of_close_from_high_to_close_gate = (buy_line_close_price - buy_line_open_price) < permissible_drop_between_open_close_price
        


        if percentage_gate and drop_from_high_to_close_gate and True:

            is_candidate = True
        else:
            is_candidate = False

        return is_candidate


# In[16]:


def find_percentage_increase_or_decrease(focused_kline_array):
    percentage_value = []
    for kline in focused_kline_array:
        diff = kline[4] - kline[1]
        perc_diff = diff/kline[1]
        percentage_value.append(perc_diff*100)
    return percentage_value 


# In[17]:


trade_list = []
init()
print('Total Tickers to Analyze')
print(len(target_ticker_list))
count = 1
for target_ticker in target_ticker_list:
    
    print('Analyzing Hourly Started ')
    print(target_ticker)

    klines = client.get_historical_klines(target_ticker, Client.KLINE_INTERVAL_1HOUR, "2 day ago UTC") 
    

    
    
    
    length = int(len(klines))
    if(length < 24):
        continue
    
    klines.pop()
    
    

    

    array = np.array(klines, dtype=np.float64)
    focused_kline_array = np.delete(array, [6, 7, 8, 9, 10, 11], 1)
    percentage_value = find_percentage_increase_or_decrease(focused_kline_array)
    percentage_value = np.reshape(percentage_value, (length -1, 1))
    focused_kline_array = np.append(focused_kline_array, percentage_value, 1)
    
    focused_reverse_kline_array = focused_kline_array[::-1]

    for x in range(0, length):
        hit_ticker_dictionary = {}
        
        filtered_klines_info = focused_reverse_kline_array[x:x+5]


        if(len(filtered_klines_info) == 5):


            
            if(is_candidate(filtered_klines_info)):

                
                
                buy_kline_info = filtered_klines_info[0]

                
                hit_ticker_dictionary = {}
                buy_price = buy_kline_info[4]
                hit_ticker_dictionary['ticker'] = target_ticker
                hit_ticker_dictionary['buy_price'] = buy_kline_info[4]

                buy_timesstamp = buy_kline_info[0]
                hit_ticker_dictionary['buy_datetime'] = str(datetime.fromtimestamp(buy_timesstamp // 1000))
                
                proft_percentage = 1.10
                loss_percentage = 0.75
                profit_sell_price = buy_price * proft_percentage
                loss_sell_price = buy_price * loss_percentage
                
                
                
                usdt = 1000
                
                buy_quantity = usdt/buy_price
                hit_ticker_dictionary['quantity'] = buy_quantity
                
                
 
                
                for y in range(0, x) :
                    
                    start = x - (y + 1)
                    end = x - y
                    
                    high_price = focused_reverse_kline_array[start:end][0][2]
                    low_price = focused_reverse_kline_array[start:end][0][3]
                    close_price = focused_reverse_kline_array[start:end][0][4]
                    sell_timesstamp = focused_reverse_kline_array[start:end][0][0]
                    sell_datetime = str(datetime.fromtimestamp(sell_timesstamp // 1000))
                    
                    if high_price >= profit_sell_price:
                        hit_ticker_dictionary['sell_price'] = profit_sell_price

                        hit_ticker_dictionary['sell_datetime'] = str(datetime.fromtimestamp(sell_timesstamp // 1000))
                        difference = focused_reverse_kline_array[start:end][0][0] - buy_kline_info[0]
                        
                        hit_ticker_dictionary['days_to_gain_loss'] = round(difference/(1000 * 60 * 24 * 60))
                        price_difference = profit_sell_price - buy_price
                        hit_ticker_dictionary['price_diff'] = price_difference
                        hit_ticker_dictionary['proft_loss'] = usdt * proft_percentage - usdt
                        break
                    elif sell_timesstamp - buy_timesstamp >= 10200000 :
                        hit_ticker_dictionary['sell_price'] = close_price

                        hit_ticker_dictionary['sell_datetime'] = str(datetime.fromtimestamp(sell_timesstamp // 1000))
                        difference = focused_reverse_kline_array[start:end][0][0] - buy_kline_info[0]
                        
                        hit_ticker_dictionary['days_to_gain_loss'] = round(difference/(1000 * 60 * 24 * 60))
                        price_difference = close_price - buy_price
                        hit_ticker_dictionary['price_diff'] = price_difference
                        hit_ticker_dictionary['proft_loss'] = buy_quantity * close_price - buy_quantity * buy_price
                        break   
                        
                trade_list.append(hit_ticker_dictionary)        
                """
                
                for y in range(x+25, length):
                    high_price = focused_kline_array[y-1:y][0][2]
                    low_price = focused_kline_array[y-1:y][0][3]
                    close_price = focused_kline_array[y-1:y][0][4]
                    sell_timesstamp = focused_kline_array[y-1:y][0][0]
                    sell_datetime = str(datetime.fromtimestamp(sell_timesstamp // 1000))


                    if high_price >= profit_sell_price:
                        hit_ticker_dictionary['sell_price'] = profit_sell_price

                        hit_ticker_dictionary['sell_datetime'] = str(datetime.fromtimestamp(sell_timesstamp // 1000))
                        difference = focused_kline_array[y-1:y][0][0] - buy_kline_info[0]
                        
                        hit_ticker_dictionary['days_to_gain_loss'] = round(difference/(1000 * 60 * 24 * 60))
                        price_difference = profit_sell_price - buy_price
                        hit_ticker_dictionary['price_diff'] = price_difference
                        hit_ticker_dictionary['proft_loss'] = usdt * proft_percentage - usdt
                        
                        break
                        
                    elif low_price <= loss_sell_price and False:
                        hit_ticker_dictionary['sell_price'] = loss_sell_price

                        hit_ticker_dictionary['sell_datetime'] = str(datetime.fromtimestamp(sell_timesstamp // 1000))
                        difference = focused_kline_array[y-1:y][0][0] - buy_kline_info[0]
                        
                        hit_ticker_dictionary['days_to_gain_loss'] = round(difference/(1000 * 60 * 24 * 60))
                        price_difference = loss_sell_price - buy_price
                        hit_ticker_dictionary['price_diff'] = price_difference
                        hit_ticker_dictionary['proft_loss'] = usdt * loss_percentage - usdt
                        break
                    elif sell_timesstamp - buy_timesstamp >= 21600000 :
                        hit_ticker_dictionary['sell_price'] = close_price

                        hit_ticker_dictionary['sell_datetime'] = str(datetime.fromtimestamp(sell_timesstamp // 1000))
                        difference = focused_kline_array[y-1:y][0][0] - buy_kline_info[0]
                        
                        hit_ticker_dictionary['days_to_gain_loss'] = round(difference/(1000 * 60 * 24 * 60))
                        price_difference = close_price - buy_price
                        hit_ticker_dictionary['price_diff'] = price_difference
                        hit_ticker_dictionary['proft_loss'] = buy_quantity * close_price - buy_quantity * buy_price
                        break
                        
                        
                        
                        
                        
               
                
                busd = 100

                quantity = busd/ buy_kline_info[4]
                quantity_str = "{:0.0{}f}".format(quantity, 2)

               
                order = client.create_test_order(symbol=target_ticker, side=SIDE_BUY, type='MARKET', quoteOrderQty=busd)
                time.sleep(5)
                order_id = order['orderId'] 
                '''order_id = client.get_all_orders(symbol=target_ticker)[0]['orderId'] '''

                buy_price = order['fills'][0]['price']
                buy_qty = order['executedQty']
                sell_price = buy_price * 1.03



                while client.get_order(symbol=target_ticker, orderId=order_id)['status'] != 'FILLED':
                    time.sleep(10)

                if client.get_order(symbol=target_ticker, orderId=order_id)['status'] == 'FILLED':
                    asset = target_ticker.split("USDT")[0]
                    balance = client.get_asset_balance(asset=asset)
                    free_to_trade = balance['free']
                    sell_price_str = "{:0.0{}f}".format(sell_price, 2)

                    order = client.create_test_order(symbol=target_ticker, side=SIDE_SELL, type='LIMIT', quantity=float(balance['free']), price=sell_price_str, timeInForce=TIME_IN_FORCE_GTC)
                    print('********** SELL ORDER SET ************************')

                    """


# In[18]:


trade_list


# In[19]:


a = 10
b = 5

step = -1 if a > b else 1
for x in range (a, b, step):
    print(x, end = ' ')


# In[20]:


len(trade_list)


# In[21]:


df = pd.DataFrame.from_dict(trade_list)


# In[22]:


print('Profit and Loss')
df['proft_loss'].sum()


# In[ ]:


print('Number of Profit Trades')
df[df['price_diff'] > 0].shape[0]


# In[ ]:


print('Number of Loss Trades')
df[df['price_diff'] < 0].shape[0]


# In[ ]:


with pd.option_context('display.max_rows', None):
    display(df.sort_values('buy_datetime'))


# In[ ]:


with pd.option_context('display.max_rows', None):
    display(df[df['price_diff'] > 0].sort_values('buy_datetime'))


# In[ ]:


with pd.option_context('display.max_rows', None):
    display(df[df['price_diff'] < 0].sort_values('buy_datetime'))


# In[ ]:


with pd.option_context('display.max_rows', None):
    display(df[pd.isna(df['sell_price'])].sort_values('buy_datetime'))


# In[ ]:


with pd.option_context('display.max_rows', None):
    display(df[np.invert(pd.isna(df['sell_price']))].sort_values('buy_datetime'))


# In[ ]:


info = client.get_symbol_info('FLMUSDT')
print(info['filters'])


# In[ ]:


print(info['filters'][0]['tickSize'])


# In[ ]:


symbol_info = {}
def get_symbol_info(symbols):
    global symbol_info
    for symbol in symbols:
        info = client.get_symbol_info(symbol)
        base_asset = info['baseAsset']
#  PRICE_FILTER
        price_filter_min_quantity = float(info['filters'][0]['minPrice'])
        price_filter_max_quantity = float(info['filters'][0]['maxPrice'])
        price_filter_tick_size = float(info['filters'][0]['tickSize'])
        
#  LOT_SIZE (for market- and limit orders)
        lot_size_min_quantity = float(info['filters'][2]['minQty'])
        lot_size_max_quantity = float(info['filters'][2]['maxQty'])
        lot_size_step_size = float(info['filters'][2]['stepSize'])
        
#  MIN NOTIONAL
        min_notional = float(info['filters'][3]['minNotional'])
        symbol_info[symbol] = {'price_filter_min_quantity': price_filter_min_quantity, 'price_filter_max_quantity': price_filter_max_quantity,                               'price_filter_tick_size': price_filter_tick_size,'lot_size_min_quantity': lot_size_min_quantity,                                 'lot_size_min_quantity': lot_size_min_quantity, 'lot_size_max_quantity': lot_size_max_quantity,                                'lot_size_step_size': lot_size_step_size, 'min_notional': min_notional, }
        


# In[ ]:




