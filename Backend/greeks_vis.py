import mibian
from Data_feeds.IBManager.option_chain_get import get_individual as get_opt
import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
pd.option_context('display.max_rows', 1000, 'display.max_columns', None)
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

import matplotlib as mpl

def greeks(pos,ticker,target_value, flag, S, K,t0,t1, r, div,px = '',IV_only = False):

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

        if px == '':
            greeks['Avg px'] = target_value
        else:
            greeks['Avg px'] = px
        greeks['DTE'] = delta.days
        greeks['pos'] = pos
        # print(greeks)
        return greeks
    else:
        return sigma


t0='20200910'
t1 ='20210115'

d1 = datetime.strptime(t1, '%Y%m%d')
d0 = datetime.strptime(t0, '%Y%m%d')


d2 = d0 + timedelta(days=1)
t0=d2.strftime('%Y%m%d')

delta = d1-d0
print(delta.days)

l = []
for i in range(-20,delta.days-1):
    d2 = d0 + timedelta(days=i)
    t0 = d2.strftime('%Y%m%d')

    print(d2)

    l.append(greeks(1,'AAPL',11.45, 'C', 112, 113,t0,t1, 0.01, 0.01,'',False))

df = pd.DataFrame(l)
print(df)


plt.plot(df['DTE'],df['theta'])
plt.axvline(delta.days)
plt.show()