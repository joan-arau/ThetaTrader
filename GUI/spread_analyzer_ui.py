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
from Backend.spread_analyzer import get_spreads
import csv
import pandas as pd
from GUI.SB_output import SB_output_GUI

tmp_file = '/Users/joan/PycharmProjects/ThetaTrader/db/temp.csv'

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/spread_analyzer_ui.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_SpreadAnalyzer, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow, Ui_SpreadAnalyzer): #gui class
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
        self.b_go_2.clicked.connect(self.get_sp)

        self.rf_rate = Qdata_feed.us_tbill_yield()['1 YR'][0]
        self.r_in.setText(str(self.rf_rate))

        self.delegate = QtWidgets.QStyledItemDelegate()
        self.pc_box.setItemDelegate(self.delegate)
        self.comboBox_2.setItemDelegate(self.delegate)




        # self.gridLayout.setSpacing(10)
        self.gridLayout.setRowStretch(10, 4)

        self.formatted_exp_list = None








    def init_ticker(self):
        self.ticker =self.ticker_in.text().upper()
        self.ticker_in.setText(self.ticker)
        # self.spot = Ydata_feed.get_latest(self.ticker)
        # self.spot_in.setText(str(self.spot['close']))
        # if spot == None:
        self.spot = data_feed.get_data(self.ticker,'STK','SMART','USD',duration ="1 D",enddate = datetime.today().strftime("%Y%m%d %H:%M:%S %Z"),barsize='1 day')
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



    def get_sp(self):
        print([self.ticker,float(self.spot_in.text()),float(self.div_in.text()),self.rf_rate,datetime.strptime(str(self.comboBox_2.currentText().split(" ")[0]),'%m-%d-%Y'),self.pc_box.currentText(),float(self.lineEdit_2.text()),float(self.lineEdit_3.text()),float(self.lineEdit.text())])
        sp = get_spreads(self.ticker,float(self.spot_in.text()),float(self.div_in.text()),self.rf_rate,datetime.strptime(str(self.comboBox_2.currentText().split(" ")[0]),'%m-%d-%Y'),self.pc_box.currentText(),float(self.lineEdit_2.text()),float(self.lineEdit_3.text()),float(self.lineEdit.text()))
        print(sp)
        max_edge = sp.iloc[0]['edge_mid']

        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().setParent(None)


        x = 0
        for row in range(0,10):
            for col in range(0,5):
                # print(round(i[1]['short'],2),'/',round(i[1]['long'],2))
                if sp.iloc[x]['edge_mid'] > 0:
                    spread = str(round(sp.iloc[x]['short'],2))+'/'+str(round(sp.iloc[x]['long'],2))+'\n'+str(round(sp.iloc[x]['credit_mid']*100,2))+'\n'+str(round(sp.iloc[x]['edge_mid'],2))
                    print(spread)
                    self.btn = QPushButton(spread, self)
                    self.btn.setToolTip('Breakeven: '+str(round(sp.iloc[x]['be'],2))+'\n'+'Max Loss: '+str(round(sp.iloc[x]['max_loss'],2))+'\n'+'POP: '+str(round(sp.iloc[x]['pop'],2)))
                    self.btn.setStyleSheet('QPushButton {background-color:rgba(0,128,0, '+str(sp.iloc[x]['edge_mid']/max_edge)+');}')
                    self.btn.clicked.connect(lambda _, pos=[[sp.iloc[x]['short'],-1],[sp.iloc[x]['long'],1]]: self.create_output(pos))
                    # self.btn.setOpacity(sp.iloc[x]['edge_mid']/max_edge)
                    self.grid.addWidget(self.btn,row,col)


                x +=1



    def create_output(self,pos):


        print(pos)
        # print(self.row_dic)
        #
        l = []
        #
        #
        #
        #
        for i in range(0,1):
            dic = {}
            dic['pc'] = str(self.pc_box.currentText())
            dic['exp'] = datetime.strptime(str(self.comboBox_2.currentText().split(" ")[0]),'%m-%d-%Y')
            dic['strike'] = pos[i][0]
            dic['amt'] = pos[i][1]

            l.append(dic)
        #
        opt_df = pd.DataFrame(l)
        # stockleg = []
        # if self.ticker_in_2.text() != '' and self.ticker_in_3.text() != '':
        #     stockleg = [float(self.ticker_in_2.text()),float(self.ticker_in_3.text())]
        # else:
        stockleg = None
        #
        stds= [self.checkBox_3.isChecked(),self.checkBox_2.isChecked()]

        # print(self.ticker, opt_df, self.rf_rate, self.div_in.text(), self.spot['close'][0], 'None', 0.5, False)
        # generate_pnl_surface(ticker=self.ticker,opt_df= opt_df,r= self.rf_rate,div= float(self.div_in.text()),s= self.spot['close'][0], strat_name=str(self.ticker+self.lineEdit_3.text()), stockleg=stockleg, pct=int(self.lineEdit_4.text())/100, threeD=self.checkBox.isChecked(),stds=stds)
        # print(self.ticker,opt_df,self.rf_rate,float(self.div_in.text()),self.spot['close'][0],str(self.ticker+self.lineEdit_3.text()), stockleg, int(self.lineEdit_4.text())/100, self.checkBox.isChecked(),stds)

        SB_output_GUI([self.ticker,opt_df,self.rf_rate,float(self.div_in.text()),self.spot['close'][0],stds,'', stockleg, int(self.lineEdit_4.text())/100, self.checkBox.isChecked()])



# [[1, 'AAPL', 10.2, 'P', 503.43, 500.0, '20200825', '20200828', 0.0014000000000000002, '0'], [1, 'AAPL', 13.88, 'C', 503.43, 500.0, '20200825', '20200828', 0.0014000000000000002, '0']]




def SAGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    SAGUI()
