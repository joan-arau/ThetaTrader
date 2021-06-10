from iexfinance.stocks import Stock
import pandas as pd
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')
import os


# token =  str(config.get('api_keys', 'iex_token'))


sandbox = False

if sandbox == True:
    os.environ["IEX_API_VERSION"] = "sandbox"
    token = 'Tpk_53da3034ca4746ee8ad133fa534eab7d'
else:
    token = 'pk_156e00bb43c64daa914260895fb9e9ba'

# token
#
# test token

# pd.set_option('display.max_columns', None)







def get_batch_prices(list_dic):
    data = list_dic
    l = []
    dic_l = []
    if type(data[0]) == dict:
        for i in data:
            # print(i,i.keys())
            l.append(list(i.keys())[0])
            dic_l.append({'Symbol':list(i.keys())[0],'conId':list(i.values())[0]})
        # print(data)
        df0 = pd.DataFrame(dic_l)
    else:
        l = data



    batch = Stock(l, token=token)
    df =  batch.get_quote()[['latestPrice']].rename_axis('Symbol').reset_index()
        # df=df
        # df = df.reset_index()
    # print(df,df0)
    if type(data[0]) == dict:
        df = pd.merge(df, df0, on='Symbol')




    return df

# print(get_batch_prices(['SPY'])['latestPrice'][0])
if __name__ == "__main__":
    # print(get_batch_prices([{'SPY':'12'},{'AAPL':'12456'}]))
    print(get_batch_prices(['SPY'])['latestPrice'][0])