import io
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
today_str = datetime.today().strftime('%Y-%m-%d')

date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

coluns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

file = 'BTC_USD.csv'
df = pd.read_csv(file)

if df.iloc[-1]['Price'] != today_str:
    new = yf.download(start=df.iloc[-1]['Price'], end=date, tickers='BTC-USD')
    new = pd.read_csv(io.StringIO(u""+new.to_csv(index=True)), header=None, skiprows=2)
    for i in range(1, len(new)):
        row = new.iloc[i]
        new_df = {
            'Price': row[0],
            'Close': float(row[1]),
            'High': float(row[2]),
            'Low': float(row[3]),
            'Open': float(row[4]),
            'Volume': int(row[5]) 
        }
        df = df._append(new_df, ignore_index=True)


    df.to_csv(file, index=False)
else:
    print('Все ок, данные уже есть')

def update_info():
    global df
    while True:
        new_info = yf.download(tickers='BTC-USD', period='1d')
        new_info = pd.read_csv(io.StringIO(u""+new_info.to_csv(index=True)), header=None, skiprows=2)
        for i in range(1, len(new_info)):
            row = new_info.iloc[i]
            new_df = {
        'Price': row[0],
        'Close': float(row[1]),
        'High': float(row[2]),
        'Low': float(row[3]),
        'Open': float(row[4]),
        'Volume': int(row[5]) 
    }   
        df.iloc[-1] = list(new_df.values())
        df.to_csv(file)
        print(df.iloc[-1])
        time.sleep(10)
update_info()

