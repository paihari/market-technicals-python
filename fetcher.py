#!/usr/bin/env python
# coding: utf-8

# In[1]:


from binance.client import Client
client = Client('', '')


# In[2]:


import numpy as np


# In[3]:


import pandas as pd


# In[4]:


from datetime import datetime


# In[5]:


usdt = 4000
eth = 0
no_of_eth_to_buy_sell = 4
buy_trades = []
sell_trades = []
profit_loss_book = 0


# In[6]:


klines = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_15MINUTE, "10 day ago UTC")


# In[7]:


print(klines)


# In[8]:


date_time = datetime.now()


# In[9]:


print(date_time)


# In[10]:


array = np.array(klines)


# In[11]:


print(array)


# In[12]:


siz = np.size(array, 0)


# In[13]:


df = pd.DataFrame.from_records(array)


# In[14]:


df.columns = ['Open Time', 'Open', 
              'High', 'Low', 'Close', 
              'Volume', 'Close Time', 
              'Quote asset volume', 'Number of trades', 
              'Taken buy base asset volume', 'Taken buy quote asset volume', 
              'Can be ignored']
df.drop(['High', 'Low', 'Quote asset volume', 'Number of trades', 
              'Taken buy base asset volume', 'Taken buy quote asset volume', 
              'Can be ignored'], axis=1, inplace=True)

df['Open Time'] = pd.to_numeric(df['Open Time'])
df['Close Time'] = pd.to_numeric(df['Close Time'])
df['Open'] = pd.to_numeric(df['Open'])
df['Close'] = pd.to_numeric(df['Close'])
df['Volume'] = pd.to_numeric(df['Volume'])

df['Is Green'] = df['Close'] > df['Open']


df['Difference'] = np.abs(df['Open'] - df['Close'])


# In[15]:


print(df)


# In[16]:


def book_profit():
    global usdt
    global profit_loss_book
    size_of_sell_trade = len(sell_trades)
    sell_price = sell_trades[size_of_sell_trade -1]
    buy_price = buy_trades[size_of_sell_trade  - 1]
    profit = sell_price - buy_price
    profit_loss_book = profit_loss_book + profit
    usdt = usdt - profit    


# In[17]:


def do_trade(typ, price, time):
    global usdt
    global eth
    global buy_trades
    global sell_trades
    
    date_time = datetime.fromtimestamp(time/1000.0)
    
    if(typ == 'BUY'):
        buy_cost = no_of_eth_to_buy_sell * price
        delta = usdt - buy_cost
        if(delta >= 0):
            usdt = usdt - buy_cost
            eth = eth + no_of_eth_to_buy_sell
            buy_trades.append(price)
            print('The Ticker price {} and Type {} remaining USDT {} ETH {} Time {}'.format(price, typ, usdt, eth, date_time))
        else:
            print('No USDT to buy ETH')
    else:
        delta = eth - no_of_eth_to_buy_sell
        if(delta >= 0):
            sell_cost = no_of_eth_to_buy_sell * price
            usdt = usdt + sell_cost
            eth = eth - no_of_eth_to_buy_sell
            sell_trades.append(price)
            book_profit()
            print('The Ticker price {} and Type {} remaining USDT {} ETH {} Time {} '.format(price, typ, usdt, eth, date_time))
        else:
            print('No ETH to Sell')
    


# In[18]:


def my_func(sliceDataFrame):
    
    no_of_records = sliceDataFrame.shape[0]
    last_candle = sliceDataFrame[-1:]
    focus_candle_frame  = sliceDataFrame.drop(sliceDataFrame.index[len(sliceDataFrame)-1])
    
    green_candles = focus_candle_frame[focus_candle_frame['Is Green'] == True]
    red_candles = focus_candle_frame[focus_candle_frame['Is Green'] == False]
    
    average_drop_of_red_candles = red_candles.nlargest(20, 'Difference')['Difference'].mean()
    average_raise_of_green_candles = green_candles.nlargest(20, 'Difference')['Difference'].mean()
    average_volume_of_red_candles = red_candles.nlargest(20, 'Volume')['Volume'].mean()
    average_volume_of_green_candles = green_candles.nlargest(20, 'Volume')['Volume'].mean()
    
    if last_candle['Is Green'].bool():
        if ((average_volume_of_green_candles < last_candle['Volume'].item()) & 
            (average_raise_of_green_candles < last_candle['Difference'].item()) &
            (average_raise_of_green_candles > average_drop_of_red_candles) & 
            (average_volume_of_green_candles > average_volume_of_red_candles)):
            sell_price = np.array(last_candle['Close'])[0]
            sell_time = np.array(last_candle['Close Time'])[0]
            print('Average raise Green candles {} Average Volume of Green candles {}'.format(average_raise_of_green_candles, average_volume_of_green_candles))
            do_trade('SELL', sell_price, sell_time)

    else:
        if ((average_volume_of_red_candles < last_candle['Volume'].item()) & 
            (average_drop_of_red_candles < last_candle['Difference'].item()) &
            (average_drop_of_red_candles > average_raise_of_green_candles) &
            (average_volume_of_red_candles > average_volume_of_green_candles)):
            buy_price = np.array(last_candle['Close'])[0]
            buy_time = np.array(last_candle['Close Time'])[0]
            print('Average drop of Red candles {} Average Volume of Red candles {}'.format(average_drop_of_red_candles, average_volume_of_red_candles))
            do_trade('BUY', buy_price, buy_time)
 


# In[19]:


j = 480
while j <= siz:
    sliceDataFrame = df[j-480: j]
    my_func(sliceDataFrame)
    j = j+1
    


# In[20]:


profit_loss_book


# In[21]:


eth


# In[22]:


usdt


# In[ ]:




