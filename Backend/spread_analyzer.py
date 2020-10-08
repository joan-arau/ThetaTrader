
import pandas as pd
import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
import datetime
import numpy as np
from scipy.stats import norm
from math import sqrt


import sys
# sys.path.append('/Users/joan/PycharmProjects')
# from stockbot.data import yahoo_data



pd.set_option('display.expand_frame_repr', False)
def greeks(target_value, flag, S, K, t1, t0, r, div, key=None, IV_only=False):
    if flag == 'C':
        call_put = 'Call'
    else:
        call_put = "Put"

    d1 = datetime.datetime.strptime(t1, '%Y%m%d')
    d0 = datetime.datetime.strptime(t0, '%Y%m%d')

    delta = d1 - d0
    delta_annual = delta.days / 365

    sigma = BSM.implied_volatility(target_value, S, K, delta_annual, r, div, flag.lower())

    if IV_only == False:
        risk_parameters = {'delta_spot': 0.02, 'delta_vol': 0.02, 'delta_rf_rate': 0.02,
                           'delta_time': 1}  # TODO Fix with next quantsbin release

        equity_o = qbdp.EqOption(option_type=call_put, strike=K, expiry_date=t1, expiry_type='American')
        engine = equity_o.engine(model="Binomial", spot0=S, pricing_date=t0,
                                 rf_rate=r, yield_div=div, volatility=sigma)

        greeks = engine.risk_parameters(**risk_parameters)
        greeks['IV'] = sigma
        greeks['key'] = key
        # print(greeks)
        return greeks
    else:
        return sigma

# ticker = 'LVS'
# exp = '20201016'
# kind = 'P'
#
# #Spread
# max_point_spread = 5
# min_otm = 0
# min_pop = 70
#
# #Underlying
# spot = 50
# div = 0.0
# r = 0.015
#

autofill = False

# if autofill == True:
#     import sys
#     sys.path.append('/Users/joan/PycharmProjects')
#     from stockbot.data import yahoo_data
#     spot = yahoo_data.get_latest(ticker)
#     div = yahoo_data.get_div_yield(ticker)






import Data_feeds.IBManager.option_chain_get as chain





def calc_put_spreads(ch,spot,div,r,t0,exp,kind,min_otm,min_pop,max_point_spread,delta_annual):

    #ch.to_csv('/Users/joanarau-schweizer/PycharmProjects/IBmanager/db/test_option_chain/20200131',index = False)

    ch = ch[ch['kind'].str.contains(kind)].sort_values(['strike'],inplace=False).reset_index(drop = True)

    ch = ch[~(ch['strike'] >= int(spot))]
    # with pd.option_context('display.max_rows', 1000, 'display.max_columns', None):
    #     print(ch)

    atm_put_IV = greeks(ch['mid'].iloc[-1],kind,spot,ch['strike'].iloc[-1],exp,t0,r,div,IV_only=True)

    l = []
    for i in range(len(ch)):

        for i1 in range(len(ch)):
            if ch['strike'][i] - ch['strike'][i1] <= max_point_spread and ch['strike'][i] - ch['strike'][i1] > 0 :
                if ch['bid'][i] >0 and ch['ask'][i] > 0 and ch['bid'][i1] >0 and ch['ask'][i1] > 0:
                    dic = {'short': ch['strike'][i] , 'long':ch['strike'][i1],'ps':ch['strike'][i] - ch['strike'][i1],'credit_ask': (ch['bid'][i] - ch['ask'][i1]),'credit_mid':((ch['bid'][i]+ch['ask'][i])/2)-((ch['bid'][i1]+ch['ask'][i1])/2),'credit_bid': (ch['ask'][i] - ch['bid'][i1])}
                    dic['be'] = dic['short'] - dic['credit_mid']
                    dic['s_p_ITM'] = norm.cdf((np.log(dic['be']/spot)/(atm_put_IV*sqrt(delta_annual))))
                    dic['l_p_ITM'] = norm.cdf((np.log(dic['long'] / spot) / (atm_put_IV * sqrt(delta_annual))))
                    dic['pop'] = (1-dic['s_p_ITM'])*100
                    dic['max_loss'] = (dic['ps']-dic['credit_mid'])*100

                    dic['edge_ask'] = (((1-dic['s_p_ITM'])*dic['credit_ask'])*100)-(dic['s_p_ITM']*dic['max_loss'])
                    dic['edge_mid'] = (((1 - dic['s_p_ITM']) * dic['credit_mid']) * 100) - (dic['s_p_ITM'] * dic['max_loss'])
                    dic['edge_bid'] = (((1 - dic['s_p_ITM']) * dic['credit_bid']) * 100) - (dic['s_p_ITM'] * dic['max_loss'])

                    if dic['pop'] >= min_pop and dic['credit_mid'] > 0.2 and (spot - dic['short']) > min_otm :
                        l.append(dic)

    spreads = pd.DataFrame(l)
    spreads = spreads[['short','long','ps','be','credit_ask','credit_mid','credit_bid','max_loss','edge_ask','edge_mid','edge_bid','s_p_ITM','l_p_ITM','pop']]
    return spreads.sort_values(['edge_mid'],inplace=False,ascending=False)


def calc_call_spreads(ch,spot,div,r,t0,exp,kind,min_otm,min_pop,max_point_spread,delta_annual):

    #ch.to_csv('/Users/joanarau-schweizer/PycharmProjects/IBmanager/db/test_option_chain/20200131',index = False)
    ch = ch[ch['kind'].str.contains(kind)].sort_values(['strike'],inplace=False,ascending=False).reset_index(drop = True)
    ch = ch[~(ch['strike'] <= spot)]

    # print(ch)

    atm_call_IV = greeks(ch['mid'].iloc[-1],kind,spot,ch['strike'].iloc[-1],exp,t0,r,div,IV_only=True)
    print('IV ', atm_call_IV)

    l = []
    for i in range(len(ch)):

        for i1 in range(len(ch)):
            if ch['strike'][i] - ch['strike'][i1] <= max_point_spread and ch['strike'][i] - ch['strike'][i1] > 0 :

                if ch['bid'][i] >0 and ch['ask'][i] > 0 and ch['bid'][i1] >0 and ch['ask'][i1] > 0:
                    dic = {'short': ch['strike'][i1] , 'long':ch['strike'][i],'ps':ch['strike'][i] - ch['strike'][i1],'credit_ask': (ch['bid'][i1] - ch['ask'][i]),'credit_mid':((ch['bid'][i1]+ch['ask'][i1])/2)-((ch['bid'][i]+ch['ask'][i])/2),'credit_bid': (ch['ask'][i1] - ch['bid'][i])}
                    dic['be'] = dic['short'] + dic['credit_mid']
                    dic['s_p_ITM'] = norm.cdf((np.log(dic['be']/spot)/(atm_call_IV*sqrt(delta_annual))))
                    dic['l_p_ITM'] = norm.cdf((np.log(dic['long'] / spot) / (atm_call_IV * sqrt(delta_annual))))
                    dic['pop'] = (1-dic['s_p_ITM'])*100
                    dic['max_loss'] = (dic['ps']-dic['credit_mid'])*100

                    dic['edge_ask'] = (((1-dic['s_p_ITM'])*dic['credit_ask'])*100)-(dic['s_p_ITM']*dic['max_loss'])
                    dic['edge_mid'] = (((1 - dic['s_p_ITM']) * dic['credit_mid']) * 100) - (dic['s_p_ITM'] * dic['max_loss'])
                    dic['edge_bid'] = (((1 - dic['s_p_ITM']) * dic['credit_bid']) * 100) - (dic['s_p_ITM'] * dic['max_loss'])
                    #print(dic)
                    #if dic['pop'] >= min_pop and dic['credit_mid'] > 0.2 and (spot - dic['short']) > min_otm :
                    l.append(dic)

    spreads = pd.DataFrame(l)
    #print(spreads)
    spreads = spreads[['short','long','ps','be','credit_ask','credit_mid','credit_bid','max_loss','edge_ask','edge_mid','edge_bid','s_p_ITM','l_p_ITM','pop']]
    return spreads.sort_values(['edge_mid'],inplace=False,ascending=False)

# spreads = calc_put_spreads()

# with pd.option_context('display.max_rows', 1000, 'display.max_columns', None):
#     print(spreads.sort_values(['edge_mid'],inplace=False,ascending=False))


def get_spreads(ticker,spot,div,r,exp,kind,min_otm,min_pop,max_point_spread):

    if kind == 'Put':
        kind = 'P'
    else:
        kind = 'C'

    t0 = datetime.datetime.today()

    delta = exp - t0
    delta_annual = delta.days / 365

    t0 = t0.strftime('%Y%m%d')
    exp = exp.strftime('%Y%m%d')

    ch = chain.get_chain(ticker, [exp])
    ch = ch[exp]
    print(ch)




    if kind == 'P':
        return calc_put_spreads(ch,spot,div,r,t0,exp,kind,min_otm,min_pop,max_point_spread,delta_annual)
    else:
        return calc_put_spreads(ch,spot,div,r,t0,exp,kind,min_otm,min_pop,max_point_spread,delta_annual)


# print(get_spreads('AMD', 113.04, 0.0, 0.12, datetime.datetime(2020, 11, 20, 0, 0), 'Put', 10.0, 70.0, 5.0))