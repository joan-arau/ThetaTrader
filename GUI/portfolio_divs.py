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
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/portfolio_divs.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

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


        self.df_div = pd.read_csv(DB_PATH+'/Dividends/IBKR-7530531.csv')

        self.df_div['payDate'] = pd.to_datetime(self.df_div['payDate'])




        # self.plt_df = self.df
        self.refresh()
        # self.create_plots()



    def create_plots(self):

        for i in reversed(range(self.gridLayout.count())):
            self.gridLayout.itemAt(i).widget().setParent(None)
        print(self.plt_df)
        self.plt_df_1 = self.plt_df.groupby('payDate', as_index=False)['grossAmount'].sum()

        self.plt_df_1['expanding']= self.plt_df_1['grossAmount'].expanding(1).sum()
        # self.plt_df_1 = self.plt_df_1.dropna(inplace=True)
        print(self.plt_df_1)

        self.plt_df_2 = self.plt_df.groupby('symbol', as_index=False)['grossAmount'].sum().sort_values('grossAmount').tail(50)
        print(self.plt_df_2)


        dates = pd.to_datetime(self.plt_df_1['payDate'])
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
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df_1['expanding'], fillLevel=0, fillBrush=(1,4),pen = (1,4),name = 'CumSum')
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash_eq'], fillLevel=0,
        #                       fillBrush=(pg.mkBrush('r')),pen=pg.mkPen('r'),name = 'Cash Eq')
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cash'], fillLevel=0, fillBrush=(2,10),pen=(2,10),name='Cash')

        # self.graphWidget.showGrid(x=True,y=True)

        self.graphWidget.setLabel('left', 'Cumulative Sum of Dividends ($)')
        # bm_date = self.bm['Date'].reset_index(drop=True)
        # print(dates,bm_date)
        # self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9,self.plt_df['cum_pct_change_y']*100, pen=pg.mkPen('b', width=2))
        # self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        # self.graphWidget.addLine(x=None, y=self.df['cum_pct_change'].iloc[-1]*100, pen=pg.mkPen('b', width=1))
        self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)



        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.grid(zorder=1,alpha=0.1)
        self.ax1.grid(zorder=1,axis='y', alpha=0.5)
        self.ax1.bar( x=self.plt_df_2['symbol'], height=self.plt_df_2['grossAmount'], align='edge', width=0.8,color ='lime' ,zorder = 3)
        for tick in self.ax1.get_xticklabels():
            tick.set_rotation(90)

        self.axes = self.ax1
        # self.fig.tight_layout()

        self.canvas = FigureCanvas(self.fig)

        self.canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.fig.tight_layout()
        self.gridLayout.addWidget(self.canvas)



        #
        #
        # win = pg.plot()
        #
        # self.graphWidget = pg.BarGraphItem(x=self.plt_df_2['symbol'], height=self.plt_df_2['grossAmount'], width=0.3, brush='r')
        # win.addItem(self.graphWidget)
        # self.gridLayout.addWidget(win)
        # # self.graphWidget.BarGraphItem(x=self.plt_df_2['symbol'], height=self.plt_df_2['grossAmount'], width=0.3, brush='r')
        #
        # # self.graphWidget.setLabel('left', 'Histogram of Returns')
        # # self.graphWidget.addLine(x=0, y=None, pen=pg.mkPen('r', width=3))
        # self.graphWidget.showGrid(x=True, y=True)
        #




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

        df = self.df_div.loc[self.df_div['payDate'] > start_date].reset_index(drop=True)



        return df











def portfolio_divsGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    portfolio_divsGUI()
