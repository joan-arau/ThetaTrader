import mibian
from Data_feeds.IBManager.option_chain_get import get_individual as get_opt
import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
import datetime
import numpy as np
import pandas as pd
pd.option_context('display.max_rows', 1000, 'display.max_columns', None)
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



def greeks(target_value, flag, S, K,t1,t0, r, div,key=None,IV_only = False):
    if flag == 'C':
        call_put = 'Call'
    else:
        call_put = "Put"

    d1 = datetime.datetime.strptime(t1,'%Y%m%d')
    d0 = datetime.datetime.strptime(t0,'%Y%m%d')



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
        greeks['IV'] = sigma
        greeks['key'] = key
        # print(greeks)
        return greeks
    else:
        return sigma




t0 = datetime.datetime.today().strftime('%Y%m%d')
t1 = '20200828'
t2=t1



r = 0.02
div = 0
s = 459

stockpos = None
#
options_list =[[['AAPL',t1,'450','C'],-1],[['AAPL',t1,'450','P'],-1]]
strat = 'Short Straddle'
#
# options_list =[[['AAPL',t1,'265','C'],-1],[['AAPL',t1,'255','P'],-1]]
# strat = 'Short Strangle'

# options_list =[[['AAPL',t1,'260','C'],-1],[['AAPL',t1,'260','P'],1]]
# strat = 'Synthetic Short'

# options_list =[[['AAPL',t1,'265','C'],-1],[['AAPL',t1,'255','C'],-1],[['AAPL',t1,'260','C'],2]]
# strat = 'Short Butterfly'
#
#options_list =[[['AMD',t2,'51','P'],2],[['AMD',t2,'50','P'],2],[['AMD',t2,'50.5','P'],-4]]
#strat = 'Butterfly'

# options_list =[[['AAPL',t1,'265','C'],-1],[['AAPL',t1,'270','C'],1],[['AAPL',t1,'255','P'],-1],[['AAPL',t1,'250','P'],1]]
# strat = None


# options_list =[[['SPY',t1,'315','C'],1]]
# strat = '1x 315Dec31 SPY P'

# options_list =[[['AAPL',t1,'260','C'],1],[['AAPL',t1,'265','C'],-1]]
# strat = '260/265 Bull Call Vertical'


# print(options_list[0][1])
opts=[]
dd= []




opt_list = []
for o in options_list:
    opt = get_opt(*o[0])
    print(opt)
    delta = datetime.datetime.strptime(o[0][1],'%Y%m%d')-datetime.datetime.strptime(t0,'%Y%m%d')
    delta_days = delta.days
    dd.append(delta_days)



    gg = greeks(opt['close'],opt['kind'],s,opt['strike'],o[0][1],t0,r,div)

    opts.append([opt,gg['IV'],delta_days,o[1]])

    opt_list.append([o[0][0]+' '+o[0][1]+' '+o[0][2]+' '+o[0][3],o[1],opt['close'],delta_days,gg['delta']*100,gg['gamma']*100,gg['theta']*100,gg['vega'],gg['rho'],gg['IV']*100])

df_cols = ['spots','dte']
if stockpos != None:
    df_cols.append('stk')
    opt_list.append(['STK',stockpos,s,0,1,0,0,0,0,0])

con_dt = pd.DataFrame(opt_list,columns = ['Contract','Position','Close','DTE','Delta','Gamma','Theta','Vega','Rho','IV'])


l = [[strat,(con_dt['Position']*con_dt['Close']).sum(),(con_dt['Position']*con_dt['Delta']).sum(),(con_dt['Position']*con_dt['Gamma']).sum(),(con_dt['Position']*con_dt['Theta']).sum(),(con_dt['Position']*con_dt['Vega']).sum(),(con_dt['Position']*con_dt['Rho']).sum()]]


strat_dt = pd.DataFrame(l,columns = ['Strategy','Cost','Delta','Gamma','Theta','Vega','Rho'])

print(strat_dt)
print(' ')
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(con_dt)
max_dd = max(dd)

# print(max_dd)

pct = 0.5

s1,s2 = [s*(1-pct),s*(1+pct)]

print(s1,s2)





for i in range(len(opts)):
    df_cols.append('pos'+str(i+1))



di = 0
dfs = []
for d in list(range(1,max_dd)):

    df = pd.DataFrame(columns=df_cols)
    df['spots'] = range(int(s1), int(s2))

    if stockpos != None:
        i = 0
        for spot in range(int(s1), int(s2)):
            df['stk'][i] = stockpos * (spot - s)
            i += 1
    n = 1
    for o in opts:
        i = 0
        for spot in range(int(s1),int(s2)):
            df['spots'][i] = spot
            dtes = o[2]- d
            if dtes >0:
                c =mibian.Me([df['spots'].iloc[i], o[0]['strike'], r*100, div*100, d], volatility=o[1]*100)

                if o[0]['kind'] == 'C':
                    df['pos' + str(n)][i] = ((c.callPrice - o[0]['close']) * o[3]) * 100
                else:
                    df['pos' + str(n)][i] = ((c.putPrice - o[0]['close']) * o[3]) * 100
            else:
                df['pos' + str(n)][i] =o[0]['close']* o[3]




            df['dte'][i] = d

            i +=1

        n+=1



    df['sum'] = df.iloc[:, -(len(df_cols) - 2):].sum(axis=1)
    # print(df)
    dfs.append(df)

    if di ==0:
        plt_df = df

    di+=1
    # print(spot,c.callPrice)
# print(dfs)
df_3d = plt_df
for f in dfs[1:]:
    df_3d=df_3d.append(f, ignore_index=True)




with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df_3d)
# #
# # # plt.plot(df['spots'],df['pos1'])
# # # plt.plot(df['spots'],df['pos2'])
plt.plot(plt_df['spots'],plt_df['sum'])
plt.plot(dfs[0]['spots'],dfs[0]['sum'])
plt.title('Payoff DTE = 1')
plt.show()
#
# #


df = df_3d

# re-create the 2D-arrays
x1 = np.linspace(df['spots'].min(), df['spots'].max(), len(df['spots'].unique()))
y1 = np.linspace(df['dte'].min(), df['dte'].max(), len(df['dte'].unique()))
x2, y2 = np.meshgrid(x1, y1)
z2 = griddata((df['spots'], df['dte']), df['sum'], (x2, y2), method='cubic')

fig = plt.figure()
ax = fig.add_subplot(111,projection='3d')
# %matplotlib

surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=plt.cm.get_cmap('RdYlGn'),linewidth=0, antialiased=False, vmin=-max(abs(df['sum'])), vmax=max(abs(df['sum'])))
fig.colorbar(surf, shrink=0.5, aspect=5)

# surf = ax.plot_wireframe(x2, y2, z2, rstride=1, cstride=1)


# ax.zaxis.set_major_locator(LinearLocator(10))
# ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
ax.view_init(15, 70)
# plt.xlim(min(df['spots']),max(df['spots']))
ax.set_ylabel('DTE')
ax.set_xlabel('Spot')
ax.set_zlabel('P&L')
ax.set_facecolor('xkcd:white')
ax.invert_xaxis()
tit = 'Payoff Surface'
if strat != None:
    tit = tit + '\n'+strat


plt.title(tit)
fig.tight_layout()
# ~~~~ MODIFICATION TO EXAMPLE ENDS HERE ~~~~ #

plt.show()