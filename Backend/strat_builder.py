import mibian
from Data_feeds.IBManager.option_chain_get import get_individual as get_opt
from Data_feeds.IBManager.historical_data import get_data
import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
from datetime import datetime
import numpy as np
import pandas as pd
pd.option_context('display.max_rows', 1000, 'display.max_columns', None)
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D
import multiprocessing as mp
from math import sqrt

from matplotlib.figure import Figure

from GUI.error import errorGUI

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



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


# print(greeks(13.49, 'P', 497, '500', 4, 0.13, 0))



def calc_pnl(spot,dte,opt_df,r,div):

    l_pnl = []

    for i in opt_df.iterrows():

        if i[1]['Contract'] == 'STK':

            l_pnl.append( (spot-i[1]['Avg px'])*i[1]['pos'] )

        else:
            c = mibian.Me([spot, i[1]['Contract'][-2], r, div * 100, dte], volatility=i[1]['IV'] * 100)

            if i[1]['Contract'][-1] == 'C':
                l_pnl.append( ((c.callPrice - i[1]['Avg px']) * i[1]['pos']) * 100)
            else:
                l_pnl.append( ((c.putPrice - i[1]['Avg px']) * i[1]['pos']) * 100)

    pnl = sum(l_pnl)

    return {'spot':spot,'dte': dte,'pnl':pnl}


















def generate_pnl_surface(ticker,opt_df,r,div,s,stds,strat_name= '',stockleg=None,pct = 0.5, threeD = False):








    dd = []
    parms = []
    t0 = datetime.today().strftime('%Y%m%d')
    r = r/100

    for o in opt_df.iterrows():

        if o[1]['pc'] == 'Put':
            kind = 'P'
        else:
            kind = 'C'

        strike = float(o[1]['strike'])

        opt = get_opt(ticker,o[1]['exp'],strike,kind)
        print(opt)

        delta = datetime.strptime(o[1]['exp'], '%Y%m%d') - datetime.strptime(t0, '%Y%m%d')
        delta_days = delta.days
        dd.append(delta_days)

        if opt['bid'] != -1 and opt['ask'] != -1:
            # midpoint
            price =  (opt['bid'] + opt['ask'])/2
        elif opt['last'] > 0: price = opt['last']
        else: price = opt['close']

        if o[1]['px'] == '':
            parms.append([o[1]['amt'],ticker,price,kind,s,strike,t0,o[1]['exp'],r,div])
        else:
            parms.append([o[1]['amt'], ticker, price, kind, s, strike, t0, o[1]['exp'], r, div,o[1]['px']])

        print(parms)





    process_pool = mp.Pool(mp.cpu_count()-1)
    ggs = process_pool.starmap(greeks, parms)
    print(opt_df,ggs)
    df_cols = ['spots', 'dte']
    if stockleg != None:
        print(stockleg)
        df_cols.append('stk')
        ggs.append({'delta': 0.01, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0, 'Contract': 'STK', 'IV': 0, 'Avg px': stockleg[1], 'DTE': 0,'pos':stockleg[0]})



    df = pd.DataFrame(ggs)
    print(df)

    df["pos"] = df["pos"].astype(int)
    l = [[strat_name, (df['pos'] * df['Avg px']).sum(), (df['pos'] * df['delta']).sum(),
          (df['pos'] * df['gamma']).sum(), (df['pos'] * df['theta']).sum(),
          (df['pos'] * df['vega']).sum(), (df['pos'] * df['rho']).sum()]]

    strat_dt = pd.DataFrame(l, columns=['Strategy', 'Cost', 'Delta', 'Gamma', 'Theta', 'Vega', 'Rho'])

    print(strat_dt)

    max_dd = max(dd)

    s1, s2 = [s * (1 - pct), s * (1 + pct)]

    parms = []

    if threeD == True:
        for i in range(1,max_dd):
            for ii in range(int(s1), int(s2)):

                parms.append([ii,i,df,r,div])
    else:

        for ii in range(int(s1), int(s2)):
            parms.append([ii, 1, df,r,div])


    pnl_l = process_pool.starmap(calc_pnl, parms)

    pnl_df = pd.DataFrame(pnl_l)


    # print(pnl_df)

    plt.style.use('dark_background')

    if stds[0] == True or stds[1] == True:
        data = get_data(ticker, 'STK', 'SMART', 'USD', duration="252 D",
                        enddate=datetime.today().strftime("%Y%m%d %H:%M:%S %Z"), barsize='1 day')
        print(data['close'].pct_change().std(), max_dd)
        st_dev = (data['close'].pct_change().std() * sqrt(max_dd))
        print(st_dev)

        return [pnl_df,df,strat_dt, st_dev]

    else:
        return [pnl_df,df,strat_dt]

    # if threeD == True:
    #     # re-create the 2D-arrays
    #     x1 = np.linspace(pnl_df['spot'].min(), pnl_df['spot'].max(), len(pnl_df['spot'].unique()))
    #     y1 = np.linspace(pnl_df['dte'].min(), pnl_df['dte'].max(), len(pnl_df['dte'].unique()))
    #     x2, y2 = np.meshgrid(x1, y1)
    #     z2 = griddata((pnl_df['spot'], pnl_df['dte']), pnl_df['pnl'], (x2, y2), method='cubic')
    #
    #     fig = plt.figure()
    #     ax = fig.add_subplot(111, projection='3d')
    #     # %matplotlib
    #
    #     surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=plt.cm.get_cmap('RdYlGn'), linewidth=0,
    #                            antialiased=False, vmin=-max(abs(pnl_df['pnl'])), vmax=max(abs(pnl_df['pnl'])))
    #     fig.colorbar(surf, shrink=0.5, aspect=5)
    #
    #     # surf = ax.plot_wireframe(x2, y2, z2, rstride=1, cstride=1)
    #
    #     # ax.zaxis.set_major_locator(LinearLocator(10))
    #     # ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
    #     ax.view_init(15, 70)
    #     # plt.xlim(min(df['spots']),max(df['spots']))
    #     ax.set_ylabel('DTE')
    #     ax.set_xlabel('Spot')
    #     ax.set_zlabel('P&L')
    #     # ax.set_facecolor('xkcd:white')
    #     ax.invert_xaxis()
    #     tit = 'Payoff Surface'
    #     if strat_name != None:
    #         tit = tit + '\n' + strat_name
    #
    #     plt.title(tit)
    #     fig.tight_layout()
    #
    #     # ~~~~ MODIFICATION TO EXAMPLE ENDS HERE ~~~~ #
    #
    #     plt.show()
    # else:
    #
    #     ax = Figure().add_subplot(111)
    #
    #
    #         #
    #         # if stds[0] == True:
    #         #     ax.axvline(x=s+(s*st_dev),linestyle='--')
    #         #     ax.axvline(x=s - (s*st_dev),linestyle='--')
    #         #
    #         # if stds[1] == True:
    #         #     ax.axvline(x=s + (s*(st_dev*2)), linestyle=':')
    #         #     ax.axvline(x=s - (s*(st_dev*2)), linestyle=':')
    #     ax.axvline(x=s, linestyle=':',color='y')
    #     ax.hlines(y=0,xmin = s1,xmax=s2, color='r')
    #
    #
    #     ax.plot(pnl_df['spot'], pnl_df['pnl'])
    #     # plt.plot(pnl_df['spots'], dfs[0]['sum'])
    #     # ax.title('Payoff DTE = 1')
    #     # plt.show()
    #
    #
    #
    #



#
#
# #
# # #
# ticker = 'AAPL'
# # #
# opt_df = pd.DataFrame([{'pc': 'Put', 'exp': datetime.strptime('08-28-2020','%m-%d-%Y').strftime('%Y%m%d'), 'strike': '500', 'amt': '1'}, {'pc': 'Call', 'exp': datetime.strptime('08-28-2020','%m-%d-%Y').strftime('%Y%m%d'), 'strike': '500', 'amt': '1'}])
# #
# # # generate_pnl_surface(ticker=ticker, opt_df=opt_df, r=0.13, div=0, s=497,strat_name='Straddle',threeD=False)
# #
# #
# #
# # opt_df = pd.DataFrame([{'pc': 'Call', 'exp': datetime.strptime('08-28-2020','%m-%d-%Y').strftime('%Y%m%d'), 'strike': '500', 'amt': '1'}])
# print(opt_df)
# generate_pnl_surface(ticker=ticker, opt_df=opt_df, r=0.13,div=0, s=497,strat_name='Straddle',threeD=False)