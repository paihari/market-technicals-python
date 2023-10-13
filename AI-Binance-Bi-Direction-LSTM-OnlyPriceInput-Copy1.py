#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tensorflow.python.keras.layers import Bidirectional, Dropout, Activation, Dense, LSTM,GRU
 
from tensorflow.keras.models import Sequential
from tensorflow.python.keras.callbacks import EarlyStopping
 
from sklearn.preprocessing import MinMaxScaler
 
from datetime import datetime

from binance.client import Client

from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json


import schedule
import time

# In[2]:


client = Client('', '')


# In[3]:


cmc = CoinMarketCapAPI('  ')


# In[4]:


info = client.get_all_tickers()


# In[5]:


'Good to check indivudual by get_symbol_info if status is trading'


# In[6]:


'Filter the Info to get the list of Symbols ending with USDT'


# In[7]:


ticker_list = [d['symbol'] for d in info if d['symbol'].endswith('USDT')]


# In[8]:


rank_info = cmc.cryptocurrency_map(sort='cmc_rank').data


# In[9]:


target_rank_info = [d['symbol']+'USDT' for d in rank_info if d['rank'] >= 200 and d['rank'] <= 400]


# In[10]:


target_ticker_list = [d for d in ticker_list if d in target_rank_info]


# In[11]:


def is_candidate(filtered_klines_info):
    context_klines_info = filtered_klines_info[0:3]
    is_candidate = True
    for context_kline in context_klines_info:
        
        volume_gate = float(context_kline[5]) * float(context_kline[4]) < 500000
        percentage_gate = (float(context_kline[1]) - float(context_kline[4]))/float(context_kline[1]) * 100 < 5

        'Get the Volume and check less than 500K Volume * Close Price' 
        'The percentage inrease in context candle should not be more than 3 percentage'
        if is_candidate and volume_gate and percentage_gate:
            is_candidate = True
        else:
            is_candidate = False
    
    trigger_kline = filtered_klines_info[-1:]
    volume_gate = float(trigger_kline[0][5]) * float(trigger_kline[0][4]) > 1000000
    percentage_gate = (5 <= (float(trigger_kline[0][1]) - 
                       float(trigger_kline[0][4]))/float(trigger_kline[0][1]) * 100 <= 10)
    if is_candidate and volume_gate and percentage_gate:
        is_candidate = True
    else:
        is_candidate = False

    return is_candidate


# In[12]:

def func():
    print('Running ...')

    for target_ticker in target_ticker_list:
        print('Fetch Data ' + target_ticker)
        klines = client.get_historical_klines(target_ticker, Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC") 
        filtered_klines_info = klines[-4:]
        if(len(filtered_klines_info) == 4 and is_candidate(filtered_klines_info)):
            print(target_ticker)


schedule.every(10).minutes.do(func)

while True:
    schedule.run_pending()
    time.sleep(1)
# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




