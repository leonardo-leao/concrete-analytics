from PyQt5 import QtCore, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')
import time

import numpy as np
from datetime import timedelta
from scipy.interpolate import make_interp_spline
from random import randrange

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
    
class MatplotlibWidgetOverview(QtWidgets.QWidget):
    
    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)

        self.graphs = {}
        self.counterGif = 0
        
        fig = Figure(dpi=90)
        fig.set_tight_layout(True)
        self.canvas = FigureCanvas(fig)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', 
                       '#17becf', '#E52B50', '#FFBF00', '#9966CC', '#0000FF', '#7FFF00', '#FF7F50', '#FFD700', '#BEBEBE', 
                       '#3FFF00', '#4B0082', '#FF00FF', '#FF4500', '#0F52BA', '#FF2400', '#00FF7F', '#D2B48C', '#92000A', 
                       '#808000', '#C8A2C8', '#29AB87', '#0047AB', '#8A2BE2', '#6F4E37', '#841B2D', '#8DB600', '#000000',
                       '#1B4D3E', '#CC5500', '#91A3B0', '#B2FFFF']
        
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
        self.setLayout(vertical_layout)

    def showGif(self, x, y):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100) #msec
        self.timer.timeout.connect(lambda: self.gif(x, y))
        self.timer.start()

    def gif(self, x, y):
        self.canvas.axes.cla()
        if self.counterGif != len(y[0]):
            x_gif = [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20]
            y_gif = []
            for i in range(len(y)):
                try:
                    y_gif.append(y[i][self.counterGif]-y[i][0])
                except:
                    y_gif.append(y_gif[-1])

            #X_Y_Spline = make_interp_spline(x_gif, y_gif)
            #x_ = np.linspace(min(x_gif), max(x_gif), 500)
            #y_ = X_Y_Spline(x_)
            self.canvas.axes.plot(x_gif, y_gif, color="C0")
            self.canvas.axes.fill_between(x_gif, y_gif, 0, color='C0', alpha=.1)
            self.canvas.axes.set_xticks(x_gif)
            self.canvas.axes.set_xlim([x_gif[0], x_gif[-1]])
            self.canvas.axes.set_ylim([-0.7, 0.7])
            self.canvas.axes.annotate(x[0][self.counterGif].strftime("%b-%d, %Y - %H:%M"), xy=(18.5, 0.5), xycoords="data",
                  va="center", ha="center",
                  bbox=dict(boxstyle="round", fc="w"))
            self.canvas.draw()
            self.counterGif += 1
        else:
            self.timer.stop()
            self.counterGif = 0

    def updatePlot(self):

        self.canvas.axes.cla()

        x = np.arange(1, 21, 1)
        y = [randrange(0, 10) for _ in range(20)]
        X_Y_Spline = make_interp_spline(x, y)
        
        x_ = np.linspace(x.min(), x.max(), 500)
        y_ = X_Y_Spline(x_)
        self.canvas.axes.plot(x_, y_, color="C0")
        self.canvas.axes.fill_between(x_, y_, y_.min(), color='C0', alpha=.1)
        self.canvas.axes.set_xticks(x)
        self.canvas.axes.set_xlim([x[0], x[-1]])
        self.canvas.axes.set_ylim([y_.min(), y_.max()*1.1])
        self.canvas.draw()

    