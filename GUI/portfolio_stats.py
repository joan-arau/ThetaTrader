import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import qdarkstyle
import pandas as pd
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
from Data_feeds.quandl import quandl_data
from datetime import datetime as dt
from datetime import timedelta
from configparser import ConfigParser
from pyfinance import ols
import matplotlib.pyplot as plt
os.environ['QT_MAC_WANTS_LAYER'] = '1'
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')
DB_PATH = config.get('main', 'path_to_db')
from scipy import stats
sys.path.append('/Users/joan/PycharmProjects')
from Stock_data_nas import get_data


dark_mode = config.get('main', 'dark_mode')
cash_equivs = config.get('main', 'cash_equivs').split(',')

# #
# import pyqtgraph.examples
# pyqtgraph.examples.run()



# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/portfolio_stats.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_Error, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow, Ui_Error): #gui class
    def __init__(self):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.setupUi(self)
        if dark_mode == 'True':
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        #set up callbacks
        # self.label.setText(label_txt)
        # self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.label.setAlignment(Qt.AlignCenter)
        # self.ui.label.setStyleSheet("QLabel {background-color: red;}")
        self.b_close.clicked.connect(self.close)
        self.refresh_b.clicked.connect(self.refresh)


        delegate = QStyledItemDelegate()
        self.comboBox.setItemDelegate(delegate)
        self.comboBox.addItems(['All extended', 'Since 2020','YTD','Trailing Month','Trailing Week'])
        self.comboBox.setCurrentIndex(2)


        self.df_pos = pd.read_csv(DB_PATH+'/Positions/IBKR-7530531.csv')
        print(self.df_pos.tail())
        self.df_pos['date'] = pd.to_datetime(self.df_pos['date'])
        self.df = pd.read_csv(DB_PATH+'/final_data/IBKR-7530531_ext.csv')
        print(self.df.tail())
        # self.bm = quandl_data.front_month_sp_futures(self.df['date'].iloc[0],self.df['date'].iloc[-1]).sort_values('Date')
        self.bm = get_data.get_data([{'symbol':'SPY','from' : pd.to_datetime(self.df['date'].iloc[0]),'to':pd.to_datetime(self.df['date'].iloc[-1])}]) #.sort_values('date')
        print(self.bm)
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.bm['date']=pd.to_datetime(self.bm['date'])
        self.bm['pct_change'] = self.bm['close'].pct_change()
        self.bm['cum_pct_change'] = (self.bm['pct_change'][1:] + 1).cumprod() - 1
        self.bm['cum_pct_change'].iloc[0] = 0
        print(self.bm.tail())
        # print(self.df)

        # print(self.df['date'],self.df['total_value'])
        # print(pd.to_datetime(self.df['date']))


        self.df= pd.merge_asof(self.df,self.bm.rename(columns={'Date':'date'}),on = 'date').dropna(subset=['date','cum_pct_change_x','cum_pct_change_y'])
        print(self.df.tail())
        window = 30
        self.df['rolling_beta'] = ols.PandasRollingOLS(y=self.df['pct_change_x'], x=self.df['pct_change_y'], window=window).beta

        self.df['rolling_std_x'] = self.df['pct_change_x'].rolling(window).std()
        self.df['rolling_std_y'] = self.df['pct_change_y'].rolling(window).std()










        # self.df = self.df.iloc[80:].reset_index(drop=True)

        # self.plt_df = self.df
        self.refresh()
        # self.create_plots()



    def create_plots(self):

        for i in reversed(range(self.gridLayout.count())):
            self.gridLayout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.gridLayout_right.count())):
            self.gridLayout_right.itemAt(i).widget().setParent(None)




        #StackPlot

        self.plt_df['cash_eq'] = 0
        for i in cash_equivs:

            cash_eq = self.df_pos.loc[self.df_pos['Symbol']==i][['date','positionValue']].reset_index(drop=True).rename(columns={'positionValue':i})

            # print(cash_eq)
            self.plt_df = pd.merge(self.plt_df, cash_eq, on='date', how='left')
            self.plt_df['cash_eq'] = self.plt_df['cash_eq']+ self.plt_df[i].fillna(0)
        # print(cash_eq)


        dates = pd.to_datetime(self.plt_df['date'])


        # print(self.plt_df)
        #
        #
        #
        # print(self.plt_df)
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})
        self.gridLayout.addWidget(self.graphWidget)
        self.graphWidget.addLegend(offset=(1,-1))
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['total_value'], fillLevel=0, fillBrush=(1,10),pen = (1,10),name = 'Total Value')
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash_eq'], fillLevel=0,
                              fillBrush=(pg.mkBrush('r')),pen=pg.mkPen('r'),name = 'Cash Eq')
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash'], fillLevel=0, fillBrush=(2,10),pen=(2,10),name='Cash')

        self.graphWidget.showGrid(x=True,y=True)

        # bm_date = self.bm['Date'].reset_index(drop=True)
        # print(dates,bm_date)
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9,self.plt_df['cum_pct_change_y']*100, pen=pg.mkPen('b', width=2))
        # self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # self.graphWidget.addLine(x=None, y=self.df['cum_pct_change'].iloc[-1]*100, pen=pg.mkPen('b', width=1))
        # self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)




        # Cash & equiv % of NAV


        self.plt_df['cash_eq%'] = (self.plt_df['cash']+self.plt_df['cash_eq'])/self.plt_df['total_value']
        # print(self.plt_df)
        dates = pd.to_datetime(self.plt_df['date'])
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})
        print(self.plt_df[['date','cash_eq']])
        self.gridLayout.addWidget(self.graphWidget)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash_eq%'] * 100)
        # self.graphWidget.setWindowTitle('Cash & Equivalents % of NAV')
        self.graphWidget.setLabel('left', 'Cash & Equivalent', units='% of NAV')
        self.graphWidget.showGrid(x=True,y=True)
        self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)

        # Rolling Beta
        # print(self.plt_df)
        dates = pd.to_datetime(self.plt_df['date'])
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})

        self.gridLayout.addWidget(self.graphWidget)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['rolling_beta'])
        # self.graphWidget.setWindowTitle('Cash & Equivalents % of NAV')
        self.graphWidget.setLabel('left', 'Rolling Beta')
        self.graphWidget.showGrid(x=True,y=True)
        self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)


        # Rolling STD
        # print(self.plt_df)
        dates = pd.to_datetime(self.plt_df['date'])
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})

        self.gridLayout.addWidget(self.graphWidget)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['rolling_std_x']*100)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['rolling_std_y']*100,pen=pg.mkPen('b'))
        # self.graphWidget.setWindowTitle('Cash & Equivalents % of NAV')
        self.graphWidget.setLabel('left', 'Rolling Std')
        self.graphWidget.showGrid(x=True,y=True)
        # self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)










        ##histogram

        ## make interesting distribution of values
        vals = np.hstack(self.plt_df['pct_change_x']*100)
        #
        # ## compute standard histogram
        y, x = np.histogram(vals,bins=51)

        vals = np.hstack(self.plt_df['pct_change_y']*100)
        #
        # ## compute standard histogram
        y1, x1 = np.histogram(vals,bins=51)





        self.graphWidget = pg.PlotWidget()
        self.gridLayout_right.addWidget(self.graphWidget)
        self.graphWidget.plot(x, y,stepMode=True, fillLevel=0, fillOutline=True, brush=pg.mkBrush('w'))
        self.graphWidget.plot(x1, -y1,stepMode=True, fillLevel=0, fillOutline=True, brush=(0, 0, 255, 150))
        self.graphWidget.setLabel('left', 'Histogram of Returns')
        self.graphWidget.addLine(x=0, y=None, pen=pg.mkPen('r', width=3))
        self.graphWidget.showGrid(x=True, y=True)





        # stonk = 'QYLD'
        # plt_df = self.df_pos.loc[(self.df_pos['underlyingSymbol']==stonk) | (self.df_pos['Symbol']==stonk)][['date','delta_pos']].reset_index(drop=True)
        # print(self.df_pos.loc[self.df_pos['underlyingSymbol']=='O'].reset_index(drop=True).head(20))
        # print(plt_df.head(20))
        #
        # date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        # self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})
        # delta = plt_df.groupby(['date']).sum().reset_index()
        # dates = pd.to_datetime(delta['date'])
        # print(delta)
        # self.gridLayout.addWidget(self.graphWidget)
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, delta['delta_pos'])
        # # self.graphWidget.setWindowTitle('Cash & Equivalents % of NAV')
        # self.graphWidget.setLabel('left', 'Position Delta'+" "+stonk)
        # self.graphWidget.showGrid(x=True,y=True)
        # self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # # self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)
        #
        # print(delta)



        # Theta/Delta
        # print(self.plt_df)

        plt_df = self.df_pos.groupby(['date'], as_index=False)['theta_pos','betaDelta'].sum()
        plt_df =plt_df[(plt_df != 0).all(1)]
        plt_df =plt_df[(np.abs(stats.zscore(plt_df[['theta_pos']])) < 3)]
        plt_df = plt_df[(np.abs(stats.zscore(plt_df[['betaDelta']])) < 3)]

        # plt.plot(plt_df['date'],plt_df['betaDelta'])
        # plt.show()
        print(plt_df)
        dates = pd.to_datetime(plt_df['date'])
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})

        self.gridLayout_right.addWidget(self.graphWidget)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, plt_df['theta_pos'])
        # self.graphWidget.setWindowTitle('Cash & Equivalents % of NAV')
        self.graphWidget.setLabel('left', 'Portfolio Theta')
        self.graphWidget.showGrid(x=True,y=True)
        self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})

        self.gridLayout_right.addWidget(self.graphWidget)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, plt_df['betaDelta'])
        # self.graphWidget.setWindowTitle('Cash & Equivalents % of NAV')
        self.graphWidget.setLabel('left', 'Portfolio Delta')
        self.graphWidget.showGrid(x=True,y=True)

        # self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)

        ## BeesPlot
        #
        # self.graphWidget = pg.PlotWidget()
        # self.gridLayout.addWidget(self.graphWidget)
        # xvals = pg.pseudoScatter(self.plt_df['pct_change_x']*100, spacing=0.4, bidir=True) * 0.2
        # self.graphWidget.plot(x=xvals, y=self.plt_df['pct_change_x']*100, pen=None, symbol='o', symbolBrush=pg.intColor(1, 6, maxValue=128))

        ## Make error bars
        # err = pg.ErrorBarItem(x=np.arange(4), y=self.plt_df['pct_change_x'].mean()*100, height=self.plt_df['pct_change_x'].std()*100, beam=0.5,
        #                       pen={'color': 'w', 'width': 2})
        # self.graphWidget.addItem(err)











    def refresh(self):


        if self.comboBox.currentText() == 'All extended':
            self.plt_df = self.df

        if self.comboBox.currentText() == 'Since 2020':
            start_date = '01.01.2020'
            self.plt_df = self.recalculate_df(start_date)
        if self.comboBox.currentText() == 'YTD':
            start_date = dt(dt.today().year, 1, 1)
            self.plt_df = self.recalculate_df(start_date)


        if self.comboBox.currentText() == 'Trailing Month':
            start_date = dt.today() - timedelta(days=31)
            self.plt_df = self.recalculate_df(start_date)

        if self.comboBox.currentText() == 'Trailing Week':
            start_date =  dt.today() - timedelta(days=7)
            self.plt_df = self.recalculate_df(start_date)

        self.create_plots()




    def recalculate_df(self, start_date):

        df = self.df.loc[self.df['date'] > start_date].reset_index(drop=True)
        print(df)
        df['cum_pct_change_x'] = (df['pct_change_x'][1:] + 1).cumprod() - 1
        df['cum_pct_change_x'].iloc[0] = 0

        df['cum_pct_change_y'] = (df['pct_change_y'][1:] + 1).cumprod() - 1
        df['cum_pct_change_y'].iloc[0] = 0

        print(df)








        return df











def portfolio_plotGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    portfolio_plotGUI()
