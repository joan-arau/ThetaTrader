import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import qdarkstyle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from configparser import ConfigParser
config = ConfigParser()
conf_path = '/Users/joan/PycharmProjects/ThetaTrader/config.ini'
config.read(conf_path)

port = int(config.get('main', 'ibkr_port'))

# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/settings_ui.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_Settings, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow, Ui_Settings): #gui class
    def __init__(self):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.setupUi(self)

        # self.port_in.setText(config.get('main', 'ibkr_port'))



        self.comboBox.addItems(['IBGW [4001]','TWS [7497]'])

        print(port)

        if port == 4001:
            self.comboBox.setCurrentIndex(0)
        else:
            self.comboBox.setCurrentIndex(1)




        self.delegate = QtWidgets.QStyledItemDelegate()
        self.comboBox.setItemDelegate(self.delegate)

        #set up callbacks

        self.b_close.clicked.connect(self.close)
        self.b_save_port.clicked.connect(self.save_port)

        self.setStyleSheet(qdarkstyle.load_stylesheet())


    def save_port(self):

        if self.comboBox.currentText() == 'IBGW [4001]':
            port = '4001'
        else:
            port = '7497'


        # port =self.port_in.text()
        config.set('main', 'ibkr_port', port)
        with open(conf_path, 'w') as f:
            config.write(f)
        # print(port)






def settingsGUI():
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    settingsGUI()