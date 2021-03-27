import mibian
from Data_feeds.IBManager.option_chain_get import get_individual as get_opt
import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
pd.option_context('display.max_rows', 1000, 'display.max_columns', None)
import matplotlib.pyplot as plt
from pylab import *
from scipy.interpolate import griddata

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import csv

import Data_feeds.IBManager.option_chain_get as chain
from Data_feeds.IBManager.option_data import main
import multiprocessing as mp

import matplotlib as mpl
from time import sleep
def greeks(pos,ticker,target_value, flag, S, K,t0,t1, r, div,px = '',IV_only = False):
    print(S)
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
        greeks['spot'] = S
        # print(greeks)
        return greeks
    else:
        return sigma


# t0='20200910'
# t1 ='20210115'
#
# d1 = datetime.strptime(t1, '%Y%m%d')
# d0 = datetime.strptime(t0, '%Y%m%d')
#
#
# d2 = d0 + timedelta(days=1)
# t0=d2.strftime('%Y%m%d')
#
# delta = d1-d0
# print(delta.days)

# l = []
# for i in range(-20,delta.days-1):
#     d2 = d0 + timedelta(days=i)
#     t0 = d2.strftime('%Y%m%d')
#
#     # print(d2)
#
#     l.append([1,'AAPL',11.45, 'C', 112, 113,t0,t1, 0.01, 0.01,'',False])


# S = 112
#
#
# for i in range(delta.days - 1):
#
#     # print(d2)
#     d2 = d0 + timedelta(days=i)
#     t0 = d2.strftime('%Y%m%d')
#     l.append([-1,'AAPL',11.45, 'C', s, 113,t0,t1, 0.01, 0.01,'',False])
#
#
#
# with mp.Pool() as pool:
#     results = pool.starmap(greeks, l)
#
#
# df = pd.DataFrame(results)
# print(df)


# plt.plot(df['DTE'],df['theta'])
# plt.axvline(delta.days)
# plt.show()

# plt.plot(df['spot'],df['gamma'])
# plt.axvline(S)
# plt.show()




ticker = 'GSX'
main(ticker)

with open('/Users/joan/PycharmProjects/ThetaTrader/db/temp.csv', newline='') as f:
    reader = csv.reader(f)
    exps = list(reader)[0]

exps = ['20201016', '20201120', '20201218']
print(exps)

# exps =['20201016','20201120']
# for exp in exps:
# chn = chain.get_chain(ticker, exps)
# print(chn)
    #
    # p = ch[ch['kind'].str.contains('P')].sort_values(['strike'], inplace=False).reset_index(drop=True)
    # c = ch[ch['kind'].str.contains('C')].sort_values(['strike'], inplace=False).reset_index(drop=True)
    # print(p,c)
    #
    # import matplotlib.pyplot as plt
    #
    # # use the scatter function
    # plt.scatter(p['strike'], -p['volume'])
    # plt.scatter(c['strike'], c['volume'])
    # plt.title(ticker+' '+exp)
    # plt.show()

while True:
    d = {}

    for i in exps:
        ch = chain.get_chain(ticker, [i])[i]
        print(ch)
        p = ch[ch['kind'].str.contains('P')].sort_values(['strike'], inplace=False).reset_index(drop=True)
        c = ch[ch['kind'].str.contains('C')].sort_values(['strike'], inplace=False).reset_index(drop=True)
        d[i] = [p,c]
        # sleep(1)



    # print(l,list(chn.keys()))
    subplots_adjust(hspace=0.000)
    number_of_subplots=len(list(d.keys()))

    fig, axs = plt.subplots(number_of_subplots, sharex=True, gridspec_kw={'hspace': 0})
    fig.suptitle(ticker)
    print(d)
    i = 0
    for x in d.keys():
        # ch = chn[x]
        # p = ch[ch['kind'].str.contains('P')].sort_values(['strike'], inplace=False).reset_index(drop=True)
        # c = ch[ch['kind'].str.contains('C')].sort_values(['strike'], inplace=False).reset_index(drop=True)
        # print(p)
        # print('\n')
        axs[i].scatter(d[x][0]['strike'], -d[x][0]['volume'])
        axs[i].scatter(d[x][1]['strike'], d[x][1]['volume'])
        axs[i].set_ylabel(x)



        i +=1

    # ax1.scatter(l[0][0]['strike'], -l[0][0]['volume'])
    # ax1.scatter(l[0][1]['strike'], l[0][1]['volume'])
    # ax1.set_ylabel(list(chn.keys())[0])
    #
    # axs[1].scatter(d['20201120'][0]['strike'], d['20201120'][0]['volume'])
    # # ax2.scatter(l[1][1]['strike'], l[1][1]['volume'])
    # axs[1].set_ylabel(list(d.keys())[1])
    #
    # ax3.scatter(l[2][0]['strike'], -l[2][0]['volume'])
    # ax3.scatter(l[2][1]['strike'], l[2][1]['volume'])
    # ax3.set_ylabel(list(chn.keys())[2])

    for ax in axs:
        ax.label_outer()



    plt.tight_layout()
    plt.show()