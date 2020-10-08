import sys
from PyQt5.QtWidgets import QApplication
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets
import qdarkstyle
from datetime import datetime
import Data_feeds.IBManager.historical_data as data_feed
import Data_feeds.YFinance.yahoo_data as Ydata_feed
import Data_feeds.quandl.quandl_data as Qdata_feed
from Data_feeds.IBManager.option_data import main as exps
from Backend.strat_builder import generate_pnl_surface
import csv
import pandas as pd
from GUI.SB_output import SB_output_GUI
from Data_feeds.IBManager.acc_data import read_positions
from configparser import ConfigParser

config = ConfigParser()
config.read('/Users/joan/PycharmProjects/ThetaTrader/config.ini')



port = int(config.get('main', 'ibkr_port'))

from ib_insync import IB

tmp_file = '/Users/joan/PycharmProjects/ThetaTrader/db/temp.csv'
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/strategy_builder_ui.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_StrategyBuilder, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow, Ui_StrategyBuilder): #gui class
    def __init__(self):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.rows = 1
        self.row_dic = {}


        self.setupUi(self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        #set up callbacks

        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)
        # self.ui.label.setStyleSheet("QLabel {background-color: red;}")

        self.b_close.clicked.connect(self.close)
        self.b_go.clicked.connect(self.init_ticker)
        self.b_new_row.clicked.connect(self.new_row)

        self.rf_rate = Qdata_feed.us_tbill_yield()['1 YR'][0]
        self.r_in.setText(str(self.rf_rate))

        self.delegate = QtWidgets.QStyledItemDelegate()
        self.pc_box.setItemDelegate(self.delegate)
        self.comboBox_2.setItemDelegate(self.delegate)

        self.bt_plt.clicked.connect(self.create_output)


        # self.gridLayout.setSpacing(10)
        self.gridLayout.setRowStretch(10, 5)

        self.formatted_exp_list = None

        self.row_dic[0] = {'+': self.b_new_row, 'PC': self.pc_box, 'exp': self.comboBox_2,
                           'strike': self.lineEdit, 'amt': self.lineEdit_2,'px':self.lineEdit_5}

        self.accs = 0

        self.positions = read_positions()


        self.fill_pos = None








    def init_ticker(self):
        self.ticker =self.ticker_in.text().upper()
        self.ticker_in.setText(self.ticker)
        # self.spot = Ydata_feed.get_latest(self.ticker)
        # self.spot_in.setText(str(self.spot['close']))
        # if spot == None:
        print(self.ticker)
        self.spot = data_feed.get_data(self.ticker,'STK','SMART','USD',duration ="1 D",enddate = datetime.today().strftime("%Y%m%d %H:%M:%S %Z"),barsize='1 day')
        sleep(5)
        self.spot_in.setText(str(self.spot['close'][0]))

        self.div_in.setText(str(0))
        # self.div_in.setText(str(Ydata_feed.get_div_yield(ticker)))

        exps(self.ticker)
        with open(tmp_file, newline='') as f:
            reader = csv.reader(f)
            self.exp_list = (datetime.strptime(i, "%Y%m%d") for i in list(reader)[0])

            self.formatted_exp_list = list((datetime.strftime(i, "%m-%d-%Y") for i in self.exp_list))
            print(list(self.formatted_exp_list),len(list(self.formatted_exp_list)))

        d0 = datetime.today() #.strftime('%Y%m%d')

        dds= []
        x = 0
        for iii in self.formatted_exp_list:
            d1 = datetime.strptime(iii,'%m-%d-%Y')#.strftime('%Y%m%d')


            delta = d1 - d0
            dd = delta.days
            dds.append(str(dd))

            self.formatted_exp_list[x] = str(self.formatted_exp_list[x]) +" ["+str(dd)+"] "
            x +=1



        print(dds,len(dds))

        print(self.formatted_exp_list)


        self.comboBox_2.addItems(self.formatted_exp_list)
        for row in self.row_dic:
            # print(row,self.row_dic[row])
            self.row_dic[row]['exp'].addItems(self.formatted_exp_list)




        if self.fill_pos == None:
            self.fill_pos = QPushButton('Fill Positions', self)
            self.horizontalLayout.addWidget(self.fill_pos)
            self.fill_pos.clicked.connect(self.fill_positions)

        ib = IB().connect('127.0.0.1', port, clientId=20)
        ib.disconnect()
        ib.waitOnUpdate(timeout=0.1)
        print('disconnected')
        print(ib.isConnected())


    def new_row(self,pc = '',exp='',strike = '',qty = '',px=''):
        # print('Clicked')

        self.new_row_btn = QPushButton('+', self)
        # self.new_row_btn.move(10, 150+ self.rows*30)
        # self.new_row_btn.setGeometry(QtCore.QRect(10, 150+ self.rows*30, 31, 21))
        # self.gridLayout.addStretch(1)
        self.gridLayout.addWidget(self.new_row_btn)
        # self.new_row_btn.show()
        self.new_row_btn.clicked.connect(self.new_row)

        #P/C Box
        self.pc_box = QtWidgets.QComboBox(self.centralwidget)
        self.pc_box.addItems(['Put','Call'])
        self.pc_box.setItemDelegate(self.delegate)
        self.gridLayout.addWidget(self.pc_box)

        if pc == 'P':
            self.pc_box.setCurrentText('Put')
        elif pc == 'C':
            self.pc_box.setCurrentText('Call')


        #exp box
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setItemDelegate(self.delegate)
        if self.formatted_exp_list != None:
            self.comboBox.addItems(self.formatted_exp_list)
        self.gridLayout.addWidget(self.comboBox)

        if exp != '':
            self.comboBox.setCurrentText(exp)


        self.lineEdit1 = QtWidgets.QLineEdit(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit1)
        self.lineEdit1.setText(str(strike))

        self.lineEdit2 = QtWidgets.QLineEdit(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit2)
        self.lineEdit2.setText(str(qty))


        self.lineEdit3 = QtWidgets.QLineEdit(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit3)
        self.lineEdit3.setText(str(px))




        self.remove_row_btn = QPushButton('-', self)
        # self.remove_row_btn.move(940, 150 + self.rows * 30)
        # self.remove_row_btn.setGeometry(QtCore.QRect(940, 150 + self.rows * 30, 31, 21))
        # self.remove_row_btn.show()

        self.gridLayout.addWidget(self.remove_row_btn)





        # print(self.row_dic)

        self.remove_row_btn.clicked.connect(lambda _, r=self.rows: self.remove_row(r))

        self.row_dic[self.rows]={'+':self.new_row_btn,'PC':self.pc_box,'exp':self.comboBox,'strike':self.lineEdit1,'amt':self.lineEdit2,'px':self.lineEdit3,'-':self.remove_row_btn}


        self.rows += 1


        self.show()




    def remove_row(self,r):

        # print(self.row_dic[r])
        # print('row: ', r)

        for item in self.row_dic[r].values():
            item.setParent(None)

        del self.row_dic[r]


    def create_output(self):

        print(self.row_dic)

        l = []




        for r in self.row_dic:
            dic = {}
            dic['pc'] = str(self.row_dic[r]['PC'].currentText())
            dic['exp'] = datetime.strptime(str(self.row_dic[r]['exp'].currentText().split(" ")[0]),'%m-%d-%Y').strftime('%Y%m%d')
            dic['strike'] = float(self.row_dic[r]['strike'].text())
            dic['amt'] = float(self.row_dic[r]['amt'].text())
            if self.row_dic[r]['px'].text() != '':
                dic['px'] = float(self.row_dic[r]['px'].text())/100
            else:
                dic['px'] = ''

            l.append(dic)

        opt_df = pd.DataFrame(l)
        stockleg = []
        if self.ticker_in_2.text() != '' and self.ticker_in_3.text() != '':
            stockleg = [float(self.ticker_in_2.text()),float(self.ticker_in_3.text())]
        else:
            stockleg = None

        stds= [self.checkBox_3.isChecked(),self.checkBox_2.isChecked()]

        # print(self.ticker, opt_df, self.rf_rate, self.div_in.text(), self.spot['close'][0], 'None', 0.5, False)
        # generate_pnl_surface(ticker=self.ticker,opt_df= opt_df,r= self.rf_rate,div= float(self.div_in.text()),s= self.spot['close'][0], strat_name=str(self.ticker+self.lineEdit_3.text()), stockleg=stockleg, pct=int(self.lineEdit_4.text())/100, threeD=self.checkBox.isChecked(),stds=stds)
        # print(self.ticker,opt_df,self.rf_rate,float(self.div_in.text()),self.spot['close'][0],str(self.ticker+self.lineEdit_3.text()), stockleg, int(self.lineEdit_4.text())/100, self.checkBox.isChecked(),stds)

        SB_output_GUI([self.ticker,opt_df,self.rf_rate,float(self.div_in.text()),self.spot['close'][0],stds,str(self.ticker+" "+self.lineEdit_3.text()), stockleg, int(self.lineEdit_4.text())/100, self.checkBox.isChecked()])

    def fill_positions(self):
        for i in reversed(list(self.row_dic.keys())):
            self.remove_row(i)
        positions = self.positions

        # accounts = positions['Account'].unique()

        positions = positions[positions['Symbol'].eq(self.ticker)]
        accounts = positions['Account'].unique()

        if self.accs ==0:
            delegate = QtWidgets.QStyledItemDelegate()
            self.accs = QtWidgets.QComboBox()
            self.accs.setItemDelegate(delegate)


            self.horizontalLayout.addWidget(self.accs)
            self.accs.addItems(accounts)


        positions = positions[positions['Account'].eq(self.accs.currentText())].drop_duplicates()

        print(positions)

        stks = positions[positions['Sec Type'].eq('STK')]
        opts = positions[positions['Sec Type'].eq('OPT')]
        d0 = datetime.today()
        for i in opts.itertuples():
            print(i)

            d1 = datetime.strptime(i.exp, '%Y%m%d')

            delta = d1 - d0
            dd = delta.days


            exp = datetime.strftime(d1,'%m-%d-%Y') + " [" + str(dd) + "] "


            self.new_row(pc = i.right,strike = i.Strike,exp=exp,qty = str(i.Quantity),px = str(i.apx))

        for i in stks.itertuples():
            self.ticker_in_2.setText(str(i.Quantity))
            self.ticker_in_3.setText(str(i.apx))


# [[1, 'AAPL', 10.2, 'P', 503.43, 500.0, '20200825', '20200828', 0.0014000000000000002, '0'], [1, 'AAPL', 13.88, 'C', 503.43, 500.0, '20200825', '20200828', 0.0014000000000000002, '0']]




def SBGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    SBGUI()
