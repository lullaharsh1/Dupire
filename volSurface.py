import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from py_vollib_vectorized import implied_volatility
import datetime
import plotly.graph_objects as go
from plotly.graph_objs import Surface
from plotly.offline import iplot, init_notebook_mode

niftyPrice=18708
opChain=pd.read_excel('NIFTYOpChain.xlsx')
dateToday = np.datetime64(datetime.datetime(2023,6,13,12,45,4)).astype('datetime64[D]')
timeToday=datetime.datetime(2023,6,13,12,45,4)
# print(opChain)
opChain.columns=['InstrumentType','ExpiryDate','OptionType','StrikePrice','Open','High','Low','Close','Prev','LTP','Chng','PerChng','Volume','Value']
print(opChain)
opChain.ExpiryDate=pd.to_datetime(opChain.ExpiryDate).astype('datetime64[D]')
opChain['tte'] = np.busday_count(dateToday,np.array(opChain['ExpiryDate'].values.astype('datetime64[D]')))/250+(datetime.datetime(2023,6,13,15,30,0) - timeToday).total_seconds()/86400/250
print(opChain)
opChain['IV'] = implied_volatility.vectorized_implied_volatility(opChain['LTP'],niftyPrice,opChain['StrikePrice'],opChain['tte'],0.00,'c',0.00)
opChain.to_csv('opChain.csv')
