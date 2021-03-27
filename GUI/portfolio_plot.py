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
config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



dark_mode = config.get('main', 'dark_mode')



# import pyqtgraph.examples
# pyqtgraph.examples.run()
# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/portfolio_plot.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

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
        self.comboBox.setCurrentIndex(0)


        self.df = pd.read_csv('/Users/joan/PycharmProjects/IBFLEX_Manager/db/final_data/IBKR:7530531_ext.csv')
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.bm_ex = True
        try:

            self.bm = quandl_data.front_month_sp_futures(self.df['date'].iloc[0],self.df['date'].iloc[-1]).sort_values('Date')
            # print(self.bm)

            self.bm['Date']=pd.to_datetime(self.bm['Date'])
            self.bm['pct_change'] = self.bm['Last'].pct_change()
            self.bm['cum_pct_change'] = (self.bm['pct_change'][1:] + 1).cumprod() - 1
            self.bm['cum_pct_change'].iloc[0] = 0
            self.df = pd.merge_asof(self.df, self.bm.rename(columns={'Date': 'date'}), on='date').dropna(subset=['date', 'cum_pct_change_x', 'cum_pct_change_y'])
            self.df=self.df.rename(columns={'cum_pct_change_x': 'cum_pct_change','cum_pct_change_y': 'cum_pct_change_bm','pct_change_x': 'pct_change','pct_change_y': 'pct_change_bm'})
        except:
            self.bm_ex = False
        # print(self.bm)
        # print(self.df)

        # print(self.df['date'],self.df['total_value'])
        # print(pd.to_datetime(self.df['date']))



        # print(df)
        # self.df = self.df.iloc[80:].reset_index(drop=True)

        self.plt_df = self.df

        self.create_plot()



    def create_plot(self):

        for i in reversed(range(self.verticalLayout.count())):
            self.verticalLayout.itemAt(i).widget().setParent(None)

        dates = pd.to_datetime(self.plt_df['date'])
        date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation='bottom')
        self.graphWidget = pg.PlotWidget(axisItems = {'bottom': date_axis})
        self.verticalLayout.addWidget(self.graphWidget,0)
        self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9, self.plt_df['cum_pct_change'] * 100)
        self.graphWidget.showGrid(x=True,y=True)
        self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)

        # bm_date = self.bm['Date'].reset_index(drop=True)
        # print(dates,bm_date)
        if self.bm_ex != False:
            self.graphWidget.plot(dates.values.astype(np.int64) // 10 ** 9,self.plt_df['cum_pct_change_bm']*100, pen=pg.mkPen('b', width=2))

        # self.graphWidget.addLine(x=None, y=self.df['cum_pct_change'].iloc[-1]*100, pen=pg.mkPen('b', width=1))


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

        self.create_plot()




    def recalculate_df(self, start_date):

        df = self.df.loc[self.df['date'] > start_date].reset_index(drop=True)
        print(df)
        df['cum_pct_change'] = (df['pct_change'][1:] + 1).cumprod() - 1
        df['cum_pct_change'].iloc[0] = 0

        if self.bm_ex != False:
            df['cum_pct_change_bm'] = (df['pct_change_bm'][1:] + 1).cumprod() - 1
            df['cum_pct_change_bm'].iloc[0] = 0

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
