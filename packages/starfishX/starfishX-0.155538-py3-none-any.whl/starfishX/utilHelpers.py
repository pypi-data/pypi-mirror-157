import pandas as pd
import numpy as np
from datetime import datetime as dt

from tvDatafeed import TvDatafeed, Interval

def isset(nameVar):
    return nameVar in globals()

def rankWithRange(data,minScope,maxScope):
    basket = data.sort_values([data.columns[0]],ascending=False)

    basket['RANK'] = list(range(len(basket), 0,-1))
    maxRank = basket['RANK'].max()
    minRank = basket['RANK'].min()
    maxScope = maxScope
    minScope = minScope
    S = (minScope-maxScope)/(minRank-maxRank)
    Int = minScope - S*minRank
    basket['RS_Rank'] = basket['RANK']*S+Int  
    
    return basket

class HistStockPrice():
  def __init__(self):    
     self.tv = TvDatafeed()
    
  def days_between(self,d1, d2):
      d1 = dt.strptime(d1, "%Y-%m-%d")
      d2 = dt.strptime(d2, "%Y-%m-%d")
      return abs((d2 - d1).days)

  def getPrice(self,symbol,start,stop='',exchange='set'):
    
      date_now = dt.today().strftime("%Y-%m-%d") 
    
      if(stop==''):
        stop = date_now
    
      k = self.days_between(start, date_now)
    
      df = self.tv.get_hist(symbol=symbol,exchange=exchange,interval=Interval.in_daily,n_bars=k)
    
      df['Date'] = pd.to_datetime(df.index)
      df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
      df['Date'] = pd.to_datetime(df['Date'])

      df = df[['Date','close']]
      df = df.set_index('Date')
      df.columns = [symbol]
    
      df = df[(df.index>=start) & (df.index<=stop)]
      return df