import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import qdarkstyle

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Backend.strat_builder import generate_pnl_surface



from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')


# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/SB_output_ui.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

SB_Output, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp1(QMainWindow,  SB_Output): #gui class
    def __init__(self,parms):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.setupUi(self)




        self.output= generate_pnl_surface(*parms)



        #set up callbacks

        self.b_close.clicked.connect(self.close)


        self.setStyleSheet(qdarkstyle.load_stylesheet())









def SB_output_GUI(parms):
    # app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)


    global window
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MyApp1(parms)
    window.show()
    # sys.exit(app.exec_())
    return window

if __name__ == "__main__":
    SB_output_GUI()