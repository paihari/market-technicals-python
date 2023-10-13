#!/usr/bin/env python
# coding: utf-8

# In[1]:


from tensorflow.python.keras.layers import Bidirectional, Dropout, Activation, Dense, LSTM,GRU
 
from tensorflow.keras.models import Sequential
from tensorflow.python.keras.callbacks import EarlyStopping
 
from sklearn.preprocessing import MinMaxScaler
 
from datetime import datetime

from binance.client import Client

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# In[2]:


client = Client('', '')


# In[3]:


klines = client.get_historical_klines("STRAXUSDT", Client.KLINE_INTERVAL_30MINUTE, "600 day ago UTC")


# In[4]:


array = np.array(klines)


# In[5]:


siz = np.size(array, 0)


# In[6]:


siz


# In[7]:


df = pd.DataFrame.from_records(array)


# In[8]:


df.columns = ['Open Time', 'Open', 
              'High', 'Low', 'Close', 
              'Volume', 'Close Time', 
              'Quote asset volume', 'Number of trades', 
              'Taken buy base asset volume', 'Taken buy quote asset volume', 
              'Can be ignored']


# In[9]:


df.drop(['Close Time', 'Can be ignored'], axis=1, inplace=True)


# In[10]:


df['Open Time'] = pd.to_numeric(df['Open Time'])/1000


# In[11]:


df['Open'] = pd.to_numeric(df['Open'])
df['High'] = pd.to_numeric(df['High'])
df['Low'] = pd.to_numeric(df['Low'])
df['Close'] = pd.to_numeric(df['Close'])
df['Volume'] = pd.to_numeric(df['Volume'])
df['Quote asset volume'] = pd.to_numeric(df['Quote asset volume'])
df['Number of trades'] = pd.to_numeric(df['Number of trades'])
df['Taken buy base asset volume'] = pd.to_numeric(df['Taken buy base asset volume'])
df['Taken buy quote asset volume'] = pd.to_numeric(df['Taken buy quote asset volume'])


# In[12]:


df['Date'] = pd.to_datetime(df['Open Time'], unit='s').dt.date


# In[13]:


group = df.groupby('Date') 


# In[14]:


df.index = df['Date']
df.info()


# In[15]:


day_price = group['Close'].mean()


# In[16]:


date1 = df['Date'][0]


# In[17]:


date1


# In[18]:


date2 = df['Date'].iloc[-1]


# In[19]:


date2


# In[20]:


delta = date2 - date1
days_look = delta.days + 1
 
data = day_price[len(day_price) - days_look:len(day_price)]
 
scl = MinMaxScaler()
 
data = data.values.reshape(data.shape[0], 1)
scale_data = scl.fit_transform(data)


# In[21]:


SEQ_LEN = 50
WINDOW_SIZE = SEQ_LEN - 1
 
BATCH_SIZE=64
 
DROPOUT = 0.2
 
 
def load_data(data_raw, seq_len):
    data = []
 
    for index in range(len(data_raw) - seq_len):
        data.append(data_raw[index: index + seq_len])
 
    data = np.array(data)
    train_split = 0.8
 
    num_data = data.shape[0]
 
    num_train = int(train_split * num_data)
 
    data = np.array(data);
 
    x_train = data[:num_train, :-1, :]
 
    y_train = data[:num_train, -1, :]
 
    x_test = data[num_train:, :-1, :]
    y_test = data[num_train:, -1, :]
 
    return [x_train, y_train, x_test, y_test]


# In[22]:


x_train, y_train, x_test, y_test = load_data(scale_data, SEQ_LEN)


# In[23]:


y_test


# In[24]:


model = Sequential()


# In[25]:


bi = Bidirectional(LSTM(WINDOW_SIZE, return_sequences=True),
                        input_shape=(WINDOW_SIZE, x_train.shape[-1]))


# In[26]:


model.add(bi)


# In[27]:


model.add(Dropout(DROPOUT))


# In[28]:


# Second Layer
model.add(Bidirectional(LSTM((WINDOW_SIZE * 2), return_sequences=True)))
model.add(Dropout(DROPOUT))


# In[29]:


# Third Layer
model.add(Bidirectional(LSTM(WINDOW_SIZE, return_sequences=False)))
model.add(Dense(units=1))


# In[30]:


# Set activation function
model.add(Activation('linear'))
model.compile(loss='mean_squared_error', optimizer='adam')


# In[31]:


print(model.summary())


# In[32]:


history = model.fit(x_train, y_train, epochs=100, batch_size=BATCH_SIZE, shuffle=False,
                    validation_data=(x_test, y_test),
                    callbacks=[EarlyStopping(monitor='val_loss', min_delta=5e-5, patience=20, verbose=1)])


# In[33]:


x_test


# In[34]:


predict_prices = model.predict(x_test)

plt.figure(figsize=(16,8))
plt.plot(scl.inverse_transform(y_test), label="Actual Values", color='green')
plt.plot(scl.inverse_transform(predict_prices), label="Predicted Values", color='red')
 
plt.title('ETH price Prediction')
plt.xlabel('time [days]')
plt.ylabel('Price')
plt.legend(loc='best')
 
plt.show()


# In[ ]:




