from PyQt5 import QtCore, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')

import numpy as np
from datetime import timedelta

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
    
class MatplotlibWidget(QtWidgets.QWidget):
    
    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)

        self.graphs = {}
        
        fig = Figure(dpi=90)
        fig.set_tight_layout(True)
        self.canvas = FigureCanvas(fig)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        vertical_layout = QtWidgets.QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3))
        self.setLayout(vertical_layout)

    def x_axes_set_date(self, x: list, split: int = 10):
        self.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d, %Y'))
        if type(x[0]) not in [int, float]:
            step = (x[0][-1] - x[0][0])/split
            self.canvas.axes.xaxis.set_ticks(np.arange(x[0][0], x[0][-1], timedelta(days=step.days, seconds=step.seconds, microseconds=step.microseconds)))
        else:
            step = (x[-1] - x[0])/split
            self.canvas.axes.xaxis.set_ticks(np.arange(x[0], x[-1], timedelta(days=step.days, seconds=step.seconds, microseconds=step.microseconds)))

    def diff(self, y: list) -> list:
        y = np.array(y)
        return y - y[0]

    def removeOutliers(self, x: list, y: list) -> list:
        diffs = self.diff(y)
        Q1, Q3 = np.quantile(diffs, 0.25), np.quantile(diffs, 0.75)
        IQR = Q3 - Q1
        minimum = Q1 - 1.5*IQR
        maximum = Q3 + 1.5*IQR
        new_x, new_y = [], []
        for i in range(len(x)):
            if minimum <= diffs[i] <= maximum:
                new_x.append(x[i]); new_y.append(y[i])
        return (new_x, new_y)

    def continuity(self, x: np.array, y: np.array):
        media_diffs = 0
        len_y = len(y)
        for i in range(len_y-1):
            media_diffs = media_diffs + abs(y[i+1] - y[i])/len_y
        new_x, new_y = [x[0]], [y[0]]
        for i in range(1, len_y-1):
            if (abs(y[i-1] - y[i]) < media_diffs*1.2 and abs(y[i] - y[i+1]) < media_diffs*1.2) or abs(new_y[-1] - y[i]) < media_diffs*1.2:
                new_x.append(x[i]); new_y.append(y[i])
        new_x.append(x[-1]); new_y.append(y[-1])
        return (new_x, new_y) 

    def plot(self, x: list, y: list, diff: bool = False, removeOutliers: bool = False, 
        continuity: bool = False, x_isDate: bool = True, labels: list = [], units: list = []):
        self.graphs = {}
        if len(x) == len(y):
            self.canvas.axes.cla()
            if x_isDate == True:
                self.x_axes_set_date(x)

            lines = []
            for i in range(len(x)):
                if diff == True:
                    y[i] = self.diff(y[i])
                if removeOutliers == True:
                    x[i], y[i] = self.removeOutliers(x[i], y[i])
                if continuity == True:
                    x[i], y[i] = self.continuity(x[i], y[i])
                label = f"Linha {i}" if labels == [] else labels[i]
                line = self.canvas.axes.plot(x[i], y[i], label=label)
                lines.append(line)

            legend = self.canvas.axes.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=4)
            lines_legend = legend.get_lines()
            for i in range(len(lines_legend)):
                lines_legend[i].set_picker(True)
                lines_legend[i].set_pickradius(5)
                self.graphs[lines_legend[i]] = lines[i][0]

            self.canvas.figure.canvas.mpl_connect("pick_event", self.on_pick)
            self.canvas.draw()
        
    def on_pick(self, event):
        legend = event.artist
        isVisible = legend.get_visible()
        self.graphs[legend].set_visible(not isVisible)
        legend.set_visible(not isVisible)
        y_max, y_min = 0, 0
        for key in self.graphs.keys():
            if self.graphs[key].get_visible():
                if y_max < max(self.graphs[key].get_ydata()):
                    y_max = max(self.graphs[key].get_ydata())
                if y_min > min(self.graphs[key].get_ydata()):
                    y_min = min(self.graphs[key].get_ydata())
        if(abs(y_min*1.1 - y_min) > abs(y_max*1.1 - y_max)):
            self.canvas.axes.set_ylim([y_min*1.1, y_max + abs(y_min*1.1 - y_min)])
        else:
            self.canvas.axes.set_ylim([y_min*1.1 - abs(y_max*1.1 - y_max), y_max*1.1])
        self.canvas.draw()
        
        
        #self.canvas.axes.clear()
        #for i in range(len(x)):
        #    self.canvas.axes.plot(x[i], y[i])
        #self.canvas.draw()