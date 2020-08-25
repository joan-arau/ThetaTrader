
import quandl
import pandas as pd
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



api_key = config.get('api_keys', 'quandl_api_key')

# print(api_key)
# breakpoint()


from datetime import date, timedelta
yesterday = str(date.today() - timedelta(days=1))

today = str(date.today())

pd.set_option('display.max_columns', None)

def front_month_sp_futures(start_date,end_date):
    d = quandl.get("CHRIS/CME_ES1", authtoken=api_key)
    d = d.reset_index(drop = False)
    d['Date'] = pd.to_datetime(d['Date'])
    d=d.sort_values('Date', ascending=False)


    mask = (d['Date'] >= start_date) & (d['Date'] <= end_date)
    d=d.loc[mask]

    return d




def us_tbill_yield():
    d =  quandl.get('USTREASURY/YIELD',authtoken=api_key,rows = 1)
    d = d.reset_index(drop=False)
    # d['Date'] = pd.to_datetime(d['Date'])
    d = d.sort_values('Date', ascending=False)
    d= d.iloc[[0]]
    d = d.reset_index(drop=True)
    d = d.drop('Date', axis=1)
    return d

def us_highQ_corporate_yield():
    d =  quandl.get('USTREASURY/HQMYC',authtoken=api_key)
    d = d.reset_index(drop=False)
    d['Month'] = pd.to_datetime(d['Month'])
    d = d.sort_values('Month', ascending=False)
    d= d.iloc[[0]]
    d = d.reset_index(drop=True)
    d = d.drop('Month', axis=1)

    return d


# print(us_tbill_yield()['1 YR'])
# us_highQ_corporate_yield()


# print(front_month_sp_futures('2018-04-18 00:00:00','2019-06-29 00:00:00')[['Date','Last']])


# print(front_month_sp_futures(yesterday,today)['Last'].iloc[0]/10)