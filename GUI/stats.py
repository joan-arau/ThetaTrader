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
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/stats.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_Error, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow, Ui_Error): #gui class
    def __init__(self,stats):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.setupUi(self)
        if dark_mode == 'True':
            plt.style.use('dark_background')
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        print(stats)
        #set up callbacks
        # self.label.setText(label_txt)
        # self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.label.setAlignment(Qt.AlignCenter)
        # self.ui.label.setStyleSheet("QLabel {background-color: red;}")
        self.b_close.clicked.connect(self.close)
        # self.refresh_b.clicked.connect(self.refresh)


        # delegate = QStyledItemDelegate()
        # self.comboBox.setItemDelegate(delegate)
        # self.comboBox.addItems(['Since 2021','YTD','Trailing Month','Trailing Week'])
        # self.comboBox.setCurrentIndex(1)
        #
        #
        # self.df_div = pd.read_csv(DB_PATH+'/Dividends/IBKR-7530531.csv')

        # self.df_div['payDate'] = pd.to_datetime(self.df_div['payDate'])
        # self.val_4.setText('$' + str(round(self.df_div['grossAmount'].sum() / ((dt.now() - self.df_div['payDate'][0]).days/30), 2)))
        # self.val_5.setText(
        #     '$' + str(round(self.df_div['grossAmount'].sum() / ((dt.now() - self.df_div['payDate'][0]).days / 7), 2)))
        # self.val_6.setText('$' + str(round(self.df_div['grossAmount'].sum()/(dt.now() - self.df_div['payDate'][0]).days, 2)))
        # print((dt.now() - self.df_div['payDate'][0]).days)

        # self.plt_df = self.df
        # self.refresh()
        # self.create_plots()

        self.label_13.setText(str(round(stats['alpha'], 2)))
        self.label_14.setText(str(round(stats['beta'], 2)))
        self.label_24.setText(str(round(stats['best_pf']*100,2))+'%')
        self.label_25.setText(str(round(stats['best_bm'] * 100, 2)) + '%')
        self.label_27.setText(str(round(stats['worst_pf']*100,2))+'%')
        self.label_28.setText(str(round(stats['worst_bm'] * 100, 2)) + '%')
        self.val_5.setText(str(round(stats['sharpe_pf'] , 2)) )
        self.label_15.setText(str(round(stats['sharpe_bm'], 2)))
        self.val_6.setText(str(round(stats['sortino_pf'], 2)))
        self.label_16.setText(str(round(stats['sortino_bm'], 2)))
        self.label_19.setText(str(round(stats['skew_pf'], 2)))
        self.label_20.setText(str(round(stats['skew_bm'], 2)))
        self.label_21.setText(str(round(stats['kurtosis_pf'], 2)))
        self.label_22.setText(str(round(stats['kurtosis_bm'], 2)))
        self.label_17.setText(str(round(stats['max_dd_pf'] * 100, 2)) + '%')
        self.label_18.setText(str(round(stats['max_dd_bm'] * 100, 2)) + '%')
        self.val_3.setText(str(round(stats['cagr_pf'] * 100, 2)) + '%')
        self.label_3.setText(str(round(stats['cagr_bm'] * 100, 2)) + '%')
        self.val_2.setText(str(round(stats['comp_pf'] * 100, 2)) + '%')
        self.label_2.setText(str(round(stats['comp_bm'] * 100, 2)) + '%')
        self.label_11.setText(str(round(stats['vol_pf'] * 100, 2)) + '%')
        self.label_12.setText(str(round(stats['vol_bm'] * 100, 2)) + '%')
    # def refresh(self):

    #
    #
    #
    #     if self.comboBox.currentText() == 'Since 2021':
    #         start_date = '01.01.2020'
    #         self.plt_df = self.recalculate_df(start_date)
    #     if self.comboBox.currentText() == 'YTD':
    #         start_date = dt(dt.today().year, 1, 1)
    #         self.plt_df = self.recalculate_df(start_date)
    #
    #
    #     if self.comboBox.currentText() == 'Trailing Month':
    #         start_date = dt.today() - timedelta(days=31)
    #         self.plt_df = self.recalculate_df(start_date)
    #
    #     if self.comboBox.currentText() == 'Trailing Week':
    #         start_date =  dt.today() - timedelta(days=7)
    #         self.plt_df = self.recalculate_df(start_date)
    #
    #     self.create_plots()
    #
    #
    #
    #
    # def recalculate_df(self, start_date):
    #
    #     df = self.df_div.loc[self.df_div['payDate'] > start_date].reset_index(drop=True)
    #     print(df)
    #     self.val_1.setText(str(len(df)))
    #     self.val_2.setText('$'+str(round(df['grossAmount'].mean(),2)))
    #     self.val_3.setText('$' + str(round(df['grossAmount'].sum(), 2)))
    #
    #
    #
    #     return df
    #










def stats_winGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    stats_winGUI()
