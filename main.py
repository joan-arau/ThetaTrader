
from GUI.error import MyApp1 as error
from GUI.settings_ui import MyApp1 as settings
from GUI.strategy_builder_ui import MyApp1 as SB
from GUI.spread_analyzer_ui import MyApp1 as SA
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import qdarkstyle

# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/TTGUI.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

Ui_ThetaTrader, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic

class MyApp(QMainWindow, Ui_ThetaTrader): #gui class
    def __init__(self):
        #The following sets up the gui via Qt
        super(MyApp, self).__init__()

        self.setupUi(self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        #set up callbacks
        self.b0.clicked.connect(self.placeholder)
        self.b1.clicked.connect(self.open_SB)
        self.b2.clicked.connect(self.open_SA)
        self.b3.clicked.connect(self.placeholder)
        self.b5.clicked.connect(self.open_settings)
        self.b4.clicked.connect(self.close)
        self.dialogs = list()

    def placeholder(self):
        dialog =error(label_txt="Error: Placeholder Button")
        self.dialogs.append(dialog)
        dialog.show()

    def open_settings(self):
        dialog = settings()
        self.dialogs.append(dialog)
        dialog.show()

    def open_SB(self):
        dialog = SB()
        self.dialogs.append(dialog)
        dialog.show()

    def open_SA(self):
        dialog = SA()
        self.dialogs.append(dialog)
        dialog.show()

if __name__ == "__main__":
    app = QApplication(sys.argv) #instantiate a QtGui (holder for the app)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())