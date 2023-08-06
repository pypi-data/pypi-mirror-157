import requests
import pandas as pd

###################### ส่วนที่ใช้ Library ภายใน ###################
try:
    #ลำดับมีผลพยายามโหลดที่ ใน folder ที่กำลัง Implement ก่อน
    #import config as con 
    from starfishX import config as con
except:
    import starfishX.config as con

prefix = "starfishX."

if(con.__mode__=="debug"):
    prefix = ""  
    
    
def getPriceAndRatioInSector(symbol,date=''):
  #resp = requests.get('https://www.settrade.com/api/set/stock/KCE/rank-in-sector?type=percentChange&date=29/04/2022')
  if(date!=''):
    date = '?type=percentChange&date='+date
    resp = requests.get('https://www.settrade.com/api/set/stock/'+symbol+'/rank-in-sector'+date)
  else:
    resp = requests.get('https://www.settrade.com/api/set/stock/'+symbol+'/rank-in-sector')
  txt = resp.json()
  df = pd.json_normalize(txt['stockTradings'])
  df['date'] = pd.to_datetime(df['date'].str[:10])
  df = df[['date','symbol','close','dividendYield','marketCap','pe','pbv']]

  return df


def listStockInSector(symbol):
  resp = requests.get('https://www.settrade.com/api/set/stock/'+symbol+'/rank-in-sector')
  txt = resp.json()
  df = pd.json_normalize(txt['stockTradings'])
  df['date'] = pd.to_datetime(df['date'].str[:10])
  df[['date','symbol','close','dividendYield','marketCap','pe','pbv']]
 
  return df[['symbol']].values.reshape(1,-1).tolist()[0]

def getRatioAndBalanceSheet(symbol):
    url = 'https://www.settrade.com/api/set/stock/'+symbol+'/company-highlight/financial-data'
    resp = requests.get(url)
    txt = resp.json()
    df = pd.json_normalize(txt)
    df['date'] = df['year'].astype(str)+df['quarter']
    #df
    #df = df[df['year']==2021]
    col = df['date']
    df = df[['date','totalAsset','totalLiability','equity','grossProfitMargin',
        'netProfitMargin','roe','roa','deRatio','eps']].T
    df.columns = col
    df = df.drop('date')
    return df

def getFundamentalInSector(symbol,year):
    '''
    symbol : str ชื่อย่อของหุ้น
    year : ปีคศ. เช่น 2021,2022 เป็นต้น
    
    date_x คือวันที่ของราคาหุ้น
    date_y คือวันที่ปิดงบ
    '''
    df1 = getPriceAndRatioInSector(symbol)
     
    s = 0
    for symbol in df1.symbol:
        df = getRatioAndBalanceSheet(symbol)
        k = ''
        for i in df.columns:
          if(str(year) in i):
             k = (i)
        if(k==''):
           continue #ถ้าไม่มีปีก็ข้ามไปเลย

        k = df[[k]].T
        k = k.reset_index()
        k['symbol'] = symbol

        if(s==0):
          df2 = k
          s=1
        else:
          df2 = df2.append(k)
        
    df = pd.merge(df1,df2,on='symbol')
    return df