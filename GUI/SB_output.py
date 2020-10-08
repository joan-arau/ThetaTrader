import sys
import os
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic
import qdarkstyle
from pyqtgraph import PlotWidget, plot
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph.opengl as gl
from Backend.strat_builder import generate_pnl_surface
from scipy.interpolate import griddata
import numpy as np



from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure



import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('QT5Agg')
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')


# path = os.path.dirname(__file__) #uic paths from itself, not the active dir, so path needed
qtCreatorFile = "/Users/joan/PycharmProjects/ThetaTrader/GUI/SB_output_ui.ui" #Ui file name, from QtDesigner, assumes in same folder as this .py

SB_Output, QtBaseClass = uic.loadUiType(qtCreatorFile) #process through pyuic


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection='3d')
        super(MplCanvas, self).__init__(self.fig)


class MyApp1(QMainWindow,  SB_Output): #gui class
    def __init__(self,parms):
        #The following sets up the gui via Qt
        super(MyApp1, self).__init__()

        self.setupUi(self)


        print(parms)


        self.label.setText(str(parms[-4]))
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setAlignment(Qt.AlignCenter)
        self.output= generate_pnl_surface(*parms)
        #
        # ax = self.canvas.figure.add_subplot(111)
        # self.canvas.figure.tight_layout()
        # ax.clear()
        # ax.plot(self.output[0]['spot'],self.output[0]['pnl'])
        # self.canvas.figure.style.use('dark_background')
        # self.canvas.draw()





        if parms[-1] == True:

            pnl_df = self.output[0]
            # glvw = gl.GLViewWidget()

            # x = np.linspace(pnl_df['spot'].min(), pnl_df['spot'].max(), len(pnl_df['spot'].unique()))
            # y = np.linspace(pnl_df['pnl'].min(), pnl_df['pnl'].max(), len(pnl_df['pnl'].unique()))
            # z = 0.1 * ((x.reshape(len(x), 1) ** 2) - (y.reshape(1, len(y)) ** 2))


            # x2, y2 = np.meshgrid(x, y)
            # z = griddata((pnl_df['spot'], pnl_df['dte']), pnl_df['pnl'], (x2, y2), method='cubic')
            # for i in z:
            #     i = i.reshape(len(x),len(y))

            # print(x,y,z)

            # x = np.linspace(self.output[0]['spot'])
            # y = np.linspace(self.output[0]['pnl'])
            # z = 0.1 * ((x.reshape(50, 1) ** 2) - (y.reshape(1, 50) ** 2))
            # p = gl.GLSurfacePlotItem(x=x, y=y, z=z, shader='normalColor')
            # p.translate(-10, -10, 0)
            # print(pnl_df)
            # x = np.linspace(pnl_df['spot'].min(), pnl_df['spot'].max(), len(pnl_df['spot'].unique()))
            # y = np.linspace(pnl_df['pnl'].min(), pnl_df['pnl'].max(), len(pnl_df['pnl'].unique()))
            # x2, y2 = np.meshgrid(x, y)
            # z = griddata((pnl_df['spot'], pnl_df['dte']), pnl_df['pnl'], (x2, y2), method='cubic')
            #
            # print(y)
            #
            # print(x)
            # print(z)
            # # cmap = plt.get_cmap('jet')
            #
            #
            # # rgba_img = cmap((temp_z - minZ) / (maxZ - minZ))
            #
            # surf = gl.GLSurfacePlotItem(x=y, y=x, z=z, shader='normalColor')
            #
            # surf.scale(3, 1, 1)
            # glvw.addItem(surf)
            # # glvw.setCameraPosition(distance=50)


            sc = MplCanvas(self, width=5, height=4, dpi=100)


            x1 = np.linspace(pnl_df['spot'].min(), pnl_df['spot'].max(), len(pnl_df['spot'].unique()))
            y1 = np.linspace(pnl_df['dte'].min(), pnl_df['dte'].max(), len(pnl_df['dte'].unique()))
            x2, y2 = np.meshgrid(x1, y1)
            z2 = griddata((pnl_df['spot'], pnl_df['dte']), pnl_df['pnl'], (x2, y2), method='cubic')

            # fig = plt.figure()
            # ax = fig.add_subplot(111, projection='3d')
            # %matplotlib

            surf = sc.axes.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap=plt.cm.get_cmap('RdYlGn'), linewidth=0,
                                   antialiased=True, vmin=-max(abs(pnl_df['pnl'])), vmax=max(abs(pnl_df['pnl'])))
            sc.fig.colorbar(surf, shrink=0.5, aspect=5)

            # surf = ax.plot_wireframe(x2, y2, z2, rstride=1, cstride=1)

            # ax.zaxis.set_major_locator(LinearLocator(10))
            # ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))
            sc.axes.view_init(15, 70)
            # plt.xlim(min(df['spots']),max(df['spots']))
            sc.axes.set_ylabel('DTE')
            sc.axes.set_xlabel('Spot')
            sc.axes.set_zlabel('P&L')
            # ax.set_facecolor('xkcd:white')
            sc.axes.invert_xaxis()
            tit = 'Payoff Surface'



            plt.title(tit)
            sc.fig.tight_layout()



            self.gridLayout.addWidget(sc,0,1)
            sc.sizeHint = lambda: pg.QtCore.QSize(100, 100)




            self.output[0]= self.output[0].loc[self.output[0]['dte'] == 1]

        self.graphWidget = pg.PlotWidget()
        self.gridLayout.addWidget(self.graphWidget,0,0)
        self.graphWidget.plot(self.output[0]['spot'],self.output[0]['pnl'])
        self.graphWidget.addLine(x=None, y=0, pen=pg.mkPen('r', width=3))
        self.graphWidget.sizeHint = lambda: pg.QtCore.QSize(100, 100)

        self.graphWidget.showGrid(x=True, y=True)

        self.graphWidget.addLine(x=parms[-6], y=None,
                                 pen=pg.mkPen('y', width=1, style=Qt.DashLine))

        if parms[-1] == True:
            sc.setSizePolicy(self.graphWidget.sizePolicy())

        if parms[-5][0] == True:

            self.graphWidget.addLine(x=parms[-6]+(self.output[-1]*parms[-6]), y=None, pen=pg.mkPen('w', width=1,style=Qt.DashLine))
            self.graphWidget.addLine(x=parms[-6] - (self.output[-1] * parms[-6]), y=None, pen=pg.mkPen('w', width=1,style=Qt.DashLine))

        if parms[-5][1] == True:
            self.graphWidget.addLine(x=parms[-6] + ((2*self.output[-1]) * parms[-6]), y=None, pen=pg.mkPen('b', width=1,style=Qt.DashLine))
            self.graphWidget.addLine(x=parms[-6] - ((2*self.output[-1]) * parms[-6]), y=None, pen=pg.mkPen('b', width=1,style=Qt.DashLine))




        l = []

        for i in self.output[1].iterrows():

            print(i[1])
            self.label =  QtWidgets.QLabel(text=str(i[1]['Contract']))
            self.gridLayout_2.addWidget(self.label)


            self.label =  QtWidgets.QLabel(text=str(round(i[1]['Avg px'],2)))
            self.gridLayout_2.addWidget(self.label)

            self.label =  QtWidgets.QLabel(text=str(round(i[1]['Avg px']*i[1]['pos'],2)))
            self.gridLayout_2.addWidget(self.label)

            l.append([i[1]['Contract'],i[1]['Avg px']*i[1]['pos']])

            self.label = QtWidgets.QLabel(text=str(round(i[1]['delta']*i[1]['pos'],2)))
            self.gridLayout_2.addWidget(self.label)

            self.label = QtWidgets.QLabel(text=str(round(i[1]['theta']*i[1]['pos'],2)))
            self.gridLayout_2.addWidget(self.label)

            self.label = QtWidgets.QLabel(text=str(round(i[1]['vega']*i[1]['pos'],2)))
            self.gridLayout_2.addWidget(self.label)

            self.label = QtWidgets.QLabel(text=str(round(i[1]['gamma']*i[1]['pos'],2)))
            self.gridLayout_2.addWidget(self.label)

            self.label = QtWidgets.QLabel(text=str(round(i[1]['IV'],2)))
            self.gridLayout_2.addWidget(self.label)

            self.label = QtWidgets.QLabel(text=str(i[1]['pos']))
            self.gridLayout_2.addWidget(self.label)



        ll = []
        for ii in l:
            if ii[0] != 'STK':
                ll.append(ii[1]*100)
            else:
                ll.append(ii[1])

        self.label_16.setText(str(round(sum(ll),2)))
        self.label_17.setText(str(round(self.output[2]['Delta'][0],2)))
        self.label_18.setText(str(round(self.output[2]['Theta'][0],2)))
        self.label_19.setText(str(round(self.output[2]['Vega'][0],2)))
        self.label_20.setText(str(round(self.output[2]['Gamma'][0],2)))
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