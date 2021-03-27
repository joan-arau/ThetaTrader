import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Data_feeds.IBManager import acc_data
from Data_feeds.IBManager import historical_data
from Data_feeds.iex import iex_data
from Data_feeds.IBManager import pnl
from Data_feeds.IBManager import option_chain_get
from datetime import datetime
import pandas as pd
import py_vollib.black_scholes_merton.implied_volatility as BSM
import quantsbin.derivativepricing as qbdp
from GUI.portfolio_plot import MyApp1 as portfolio_plot
from GUI.portfolio_stats import MyApp1 as portfolio_stats
os.environ['QT_MAC_WANTS_LAYER'] = '1'
from configparser import ConfigParser
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



dark_mode = config.get('main', 'dark_mode')


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option("display.width", 200)
# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/portfolio_manager.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_pm, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

def greeks(pos,ticker,target_value, flag, S, K,t0,t1, r, div,px = '',IV_only = False):
    # print(S)
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




class MyApp1(QMainWindow, Ui_pm): #gui class




    def __init__(self):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()
        self.setupUi(self)
        self.dialogs = list()
        self.account = 'U7530531'
        # self.account = 'U3266425'

        # self.positions['value'] = self.positions['value']



        # print(self.positions)




        self.b_close.clicked.connect(self.close)
        self.b_plot.clicked.connect(self.portfolio_plt)
        self.b_stats.clicked.connect(self.portfolio_stats)

        # self.get_position_details()

        print(dark_mode)
        if dark_mode == 'True':
            self.setStyleSheet(qdarkstyle.load_stylesheet())

    def portfolio_plt(self):
        dialog = portfolio_plot()
        self.dialogs.append(dialog)
        dialog.show()

    def portfolio_stats(self):
        dialog = portfolio_stats()
        self.dialogs.append(dialog)
        dialog.show()



    def get_position_details(self):
        always_refresh = False

        # print(os.listdir('/Users/joan/PycharmProjects/ThetaTrader/db/accounts')[self.account*])
        result = list(filter(lambda x: x.startswith(self.account), os.listdir('/Users/joan/PycharmProjects/ThetaTrader/db/accounts')))

        try:
            diff =(datetime.now() -datetime.strptime(result[0].split('_')[-1].split('.')[0],'%m%d%Y%H%M%S')).total_seconds() /3600
            print(diff)
        except:
            print('file not found, downloading positions')
            diff = 10


        if diff >1 or always_refresh == True:

            self.positions = acc_data.read_positions()


            self.positions=self.positions.loc[self.positions['Account'] == self.account]
            self.positions['delta'] = ''
            df = self.positions
            df1 = pnl.main(self.account)

            # print(df,df1)
            df3 = pd.merge(df, df1, on='conId', how='left').drop_duplicates(subset=['conId'])
            self.positions = df3
            df = self.positions.loc[self.positions['Sec Type'] == 'STK'][['Symbol', 'conId', 'exchange']]
            # df.to_csv('/Users/joan/PycharmProjects/ThetaTrader/db/conIds.csv')
            df_old = pd.read_csv('/Users/joan/PycharmProjects/ThetaTrader/db/conIds.csv', index_col=0)
            # print(df_old, df)
            df_new = pd.concat([df_old, df]).drop_duplicates(subset=['Symbol'], keep='first')
            if len(df_new) !=len(df_old):
                df_new.to_csv('/Users/joan/PycharmProjects/ThetaTrader/db/conIds.csv')


            # print(df3)
            dic_l = []
            for row in df3.iterrows():
                # print(row[1]['Symbol'])
                if row[1]['Sec Type'] == 'STK':
                    dic_l.append({'conId':row[1]['conId'],'delta':row[1]['Quantity']})

                elif row[1]['Sec Type'] == 'OPT':
                    try:
                        # print(row[1]['Symbol'])
                        try:
                            px = df3.loc[df3['Sec Type'] == 'STK'].loc[df3['Symbol'] == row[1]['Symbol']].reset_index(drop=True)['price'].iloc[0]
                            print(row[1]['Symbol'],px,' DF')
                        except:
                            try:
                                px = iex_data.get_batch_prices([row[1]['Symbol']])['latestPrice'][0]
                                print(row[1]['Symbol'],px,' IEX')
                            except:

                                # print(df_new.loc[df_new['Symbol'] == row[1]['Symbol']]['conId'].iloc[0],
                                #       df_new.loc[df_new['Symbol'] == row[1]['Symbol']]['exchange'].iloc[0])
                                try:

                                    px = historical_data.get_data(conid=df_new.loc[df_new['Symbol'] == row[1]['Symbol']]['conId'].iloc[0],exch=df_new.loc[df_new['Symbol'] == row[1]['Symbol']]['exchange'].iloc[0],duration ="1 D",enddate = datetime.today().strftime("%Y%m%d %H:%M:%S %Z"),barsize='1 day')['close'].iloc[0]
                                    print(row[1]['Symbol'], px,' IBKR')
                                except:
                                    print('no px found: ',row[1]['Symbol'])
                        delta = greeks(row[1]['Quantity'], row[1]['Symbol'], row[1]['price']/100, row[1]['right'],
                                       px, row[1]['Strike'],
                                       datetime.today().strftime('%Y%m%d'), row[1]['exp'], 0.01, 0.01)
                        print(row[1]['Symbol'],delta)
                        dic_l.append({'conId': row[1]['conId'], 'delta': row[1]['Quantity']*(delta['delta']*100)})
                    except:
                        pass

            df3 = pd.merge(df3, pd.DataFrame(dic_l), on='conId', how='left')
            df3 = df3.drop(['primary_exchange', 'secId', 'secId_type', 'delta_x'], axis=1)
            df3 =df3.rename(columns={"delta_y": "delta",})
            # print(df3)
            df3.to_csv('/Users/joan/PycharmProjects/ThetaTrader/db/accounts/'+ self.account+'_'+ datetime.now().strftime('%m%d%Y%H%M%S')+'.csv')
            self.positions = df3

        else:
            self.positions = pd.read_csv('/Users/joan/PycharmProjects/ThetaTrader/db/accounts/'+result[0],index_col=0)



        print(self.positions.sort_values('Symbol'))




def portfolio_manager_GUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    portfolio_manager_GUI()

