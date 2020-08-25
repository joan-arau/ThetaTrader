from yahoofinancials import YahooFinancials

import pandas as pd


def get_div_yield(symbol):

    stock = YahooFinancials(symbol)
    if stock.get_dividend_yield() !=None:
        y= stock.get_dividend_yield()
    elif stock.get_summary_data()[symbol]  !=None:
        y= stock.get_summary_data()[symbol]['yield']
    else: y= 0

    if y== None :
        return 0
    else: return y


def get_historical(symbol,start,end):
    stock = YahooFinancials(symbol)

    return pd.DataFrame.from_dict(stock.get_historical_price_data(start, end, 'daily')[symbol]['prices']).rename(index=str, columns={'adjclose':'adjClose'})

# print(get_historical('SPY','20100505','20190505'))

def get_latest(symbol):
    stock = YahooFinancials(symbol)
    return stock.get_current_price()

# print(get_div_yield('SPY'))
# print(get_latest('AAPL'))