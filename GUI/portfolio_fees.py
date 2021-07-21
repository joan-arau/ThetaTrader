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
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import matplotlib.pyplot as plt
from pyfinance import ols
os.environ['QT_MAC_WANTS_LAYER'] = '1'
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')
DB_PATH = config.get('main', 'path_to_db')

sys.path.append('/Users/joan/PycharmProjects')
from Stock_data_nas import get_data


dark_mode = config.get('main', 'dark_mode')
cash_equivs = config.get('main', 'cash_equivs').split(',')

# #
# import pyqtgraph.examples
# pyqtgraph.examples.run()



# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/portfolio_fees.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_Error, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow, Ui_Error): #gui class
    def __init__(self):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.setupUi(self)
        if dark_mode == 'True':
            plt.style.use('dark_background')
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
        self.comboBox.addItems(['Since 2021','YTD','Trailing Month','Trailing Week'])
        self.comboBox.setCurrentIndex(1)


        # self.df_div = pd.read_csv(DB_PATH+'/Dividends/IBKR-7530531.csv')

        self.CT = pd.read_csv(DB_PATH+'/Fees/IBKR-7530531-CashTransactions.csv',index_col='date',parse_dates=['date'])
        self.CC = pd.read_csv(DB_PATH + '/Fees/IBKR-7530531-Commissions.csv',index_col='date',parse_dates=['date'])
        self.ID = pd.read_csv(DB_PATH + '/Fees/IBKR-7530531-Interest.csv',index_col='date',parse_dates=['date'])
        self.SLB = pd.read_csv(DB_PATH + '/Fees/IBKR-7530531-SLB.csv',index_col='date',parse_dates=['date'])


        print(self.CC,self.CT)
        self.ct = self.CT[['amount_base']].groupby(pd.Grouper(freq='d')).sum()
        self.cc = self.CC[['totalCommission_base']].groupby(pd.Grouper(freq='d')).sum()
        # self.id = self.ID[['totalInterest_base']].groupby(pd.Grouper(freq='d')).sum()
        self.slb = self.SLB[['Fee_base']].groupby(pd.Grouper(freq='d')).sum()


        self.merge = self.slb
        self.merge = self.merge.merge(self.cc,on = 'date')
        self.merge = self.merge.merge(self.ct, on='date')
        print(self.merge)



        self.val_4.setText('$' + str(round(self.merge['amount_base'].sum())))
        self.val_5.setText(
            '$' + str(round(self.merge['totalCommission_base'].sum())))
        self.val_6.setText('$' + str(round(self.merge['Fee_base'].sum())))
        # self.label_2.setText('$' + str(round(self.merge['totalInterest_base'].sum())))
        self.label_6.setText('$' + str(round(self.merge['Fee_base'].sum()+self.merge['totalCommission_base'].sum()+self.merge['amount_base'].sum())))
        # self.plt_df = self.df
        self.refresh()
        # self.create_plots()

        # breakpoint()


    def create_plots(self):

        for i in reversed(range(self.gridLayout.count())):
            self.gridLayout.itemAt(i).widget().setParent(None)



        self.plt_df['expanding_1']= self.plt_df['amount_base'].expanding(1).sum()
        self.plt_df['expanding_2'] = self.plt_df['totalCommission_base'].expanding(1).sum()
        self.plt_df['expanding_3'] = self.plt_df['Fee_base'].expanding(1).sum()

        # self.plt_df_1 = self.plt_df_1.dropna(inplace=True)
        print(self.plt_df)



        dates = pd.to_datetime(self.plt_df.index)
        #
        #
        # # print(self.plt_df)
        # #
        # #
        # #
        # # print(self.plt_df)
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})
        self.gridLayout.addWidget(self.graphWidget)
        self.graphWidget.addLegend(offset=(1,-1))

        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, -self.plt_df['expanding_2'], fillLevel=0,
                              fillBrush=(1, 6), pen=(1, 6), name='Commission')
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, -self.plt_df['expanding_1'], fillLevel=1, fillBrush=(1,4),pen = (1,4),name = 'Data,Research,Interest')
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, -self.plt_df['expanding_3'], fillLevel=1,
                              fillBrush=(1, 8), pen=(1, 8), name='SLB Fees')
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, -self.plt_df['expanding_2']-self.plt_df['expanding_1']-self.plt_df['expanding_3'], fillLevel=0,
                               pen='r', name='Total Fees')

        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash_eq'], fillLevel=0,
        #                       fillBrush=(pg.mkBrush('r')),pen=pg.mkPen('r'),name = 'Cash Eq')
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash'], fillLevel=0, fillBrush=(2,10),pen=(2,10),name='Cash')

        # self.graphWidget.showGrid(x=True,y=True)

        self.graphWidget.setLabel('left', 'Total Fees ($)')
        # bm_date = self.bm['Date'].reset_index(drop=True)
        # print(dates,bm_date)
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9,self.plt_df['cum_pct_change_y']*100, pen=pg.mkPen('b', width=2))
        # self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # self.graphWidget.addLine(x=None, y=self.df['cum_pct_change'].iloc[-1]*100, pen=pg.mkPen('b', width=1))
        self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)












    def refresh(self):



        if self.comboBox.currentText() == 'Since 2021':
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

        df = self.merge.loc[self.merge.index > start_date]
        print(df)
        self.val_1.setText(str(len(df)))
        self.val_2.setText('$'+str(round(df['amount_base'].mean(),2)))
        self.val_3.setText('$' + str(round(df['amount_base'].sum(), 2)))



        return df











def portfolio_divsGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    portfolio_divsGUI()
