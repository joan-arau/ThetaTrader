
from configparser import ConfigParser

config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')
import sys,os
sys.path.append('/Users/joan/PycharmProjects')

from Stock_data_nas import get_data

from Data_feeds.IBManager import option_chain_get
from Data_feeds.IBManager import ratios






from ib_insync import *
import pandas as pd

import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
import mibian

from datetime import datetime,timedelta


from multiprocessing import Pool
import multiprocessing
import math
from datetime import datetime as time


def greeks(idx,ticker,target_value, flag, S, K,t0,t1, r, div,IV_only = False):
    try:
        if flag == 'C':
            call_put = 'Call'
        else:
            call_put = "Put"

        d1 = datetime.strptime(t1,'%Y%m%d')
        d0 = datetime.strptime(t0,'%Y%m%d')



        delta = d1-d0
        delta_annual = delta.days / 365


        sigma = BSM.implied_volatility(target_value, S, K, delta_annual, r, div, flag.lower())

        if IV_only == False:
            risk_parameters = {'delta_spot': 0.02, 'delta_vol': 0.02, 'delta_rf_rate': 0.02,
                               'delta_time': 1}  # TODO Fix with next quantsbin release


            equity_o = qbdp.EqOption(option_type=call_put, strike=K, expiry_date=t1, expiry_type='American')
            engine = equity_o.engine(model="Binomial", spot0=S, pricing_date=t0,
                                     rf_rate=r, yield_div=div, volatility=sigma)

            greeks = engine.risk_parameters(**risk_parameters)
            greeks['Contract'] = [ticker,t1,str(K),flag]
            greeks['IV'] = sigma

            greeks['DTE'] = delta.days
            greeks['index'] = idx
            # print(greeks)
            return greeks
        else:
            return sigma
    except:
        return {'delta': None, 'gamma': None, 'theta': None, 'vega': None, 'rho': None, 'Contract': None, 'IV': None, 'DTE': None, 'index': None}

def get_chain_w_greeks(ticker,exp_list = None,r = None,div = None,spot = None,ib = None):

    if r == None:
        r = 0.01

    if spot == None:
        print(ticker)
        spot = get_data.get_data([{'symbol':'AAPL','from':(datetime.today()-timedelta(1)),'to': datetime.today()}],ib=ib)['close'].iloc[-1]



        print(spot)

    if div == None:
        try:
            div = ratios.get_ratios([ticker], ['YIELD'])['YIELD'][0]
        except:
            div = 0.01
    print(div)
    chain = option_chain_get.get_chain(ticker,exp_list)
    print(chain)

    # if div == None:
        # try:







    df_list = []
    for key in chain.keys():
        df = chain[key]
        df['exp'] = key
        df_list.append(df)

    df = pd.concat(df_list).reset_index(drop=True).reset_index()
    print(df,div)
    t0 =datetime.today().strftime("%Y%m%d")
    input_list = []
    for i,row in df.iterrows():
        input_list.append((row['index'],ticker,row['mid'], row['kind'], spot, row['strike'],t0,row['exp'], r, float(div)/100,False))
    #
    #

    print(input_list)
    print('CPU Cores: '+str(multiprocessing.cpu_count()))

    with multiprocessing.Pool() as pool:
        var = pool.starmap(greeks, input_list)
    # print(var)
    greek_df=pd.DataFrame(var)
    print(greek_df)
    merge= df.merge(greek_df,on= 'index')
    merge=merge.drop(columns=['index'])
    print(merge)
    return merge

    # var = range(500)

# t1 = time.now()
if __name__ == '__main__':
    port = int(config.get('main', 'ibkr_port'))
    ib = IB()
    import random

    ib.connect('127.0.0.1', port, clientId=random.randint(0, 9999))

    print(get_chain_w_greeks('AAPL',['20210917'],ib=ib))

    ib.disconnect()
    # print(greeks('AAPL', 30.299999999999997, 'C', 120.07, 90.0, '20210319', '20210416', 0.01, 0.6613436, False))

# exp_list = ['20210416','20210430']
# with multiprocessing.Pool(processes=3) as pool:
#     var = pool.starmap(greeks, [('AAPL', 30.225, 'C', 120.02, 90.0, '20210319', '20210416', 0.01, 0.6613436, False), ('AAPL', 29.0, 'C', 120.02, 91.25, '20210319', '20210416', 0.01, 0.6613436, False)])
# print(var)
# print('Time: '+str(time.now()-t1))
