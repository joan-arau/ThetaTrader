import datetime
from ib_insync import *
import pandas as pd
pd.set_option('display.max_columns', None)
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')

port = int(config.get('main', 'ibkr_port'))

ib = IB()
ib.connect('127.0.0.1', port, clientId=1)



### TODO

contract = Stock('SPY', 'SMART', 'USD')

dt = ''
barsList = []

bars = ib.reqHistoricalData(
    contract,
    endDateTime=dt,
    durationStr='10 D',
    barSizeSetting='1 day',
    whatToShow= 'OPTION_IMPLIED_VOLATILITY',
    useRTH=False,
    formatDate=1)
print(bars)
df = util.df(bars)

print(df)