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

        self.secondAxe = None
        
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
            if self.secondAxe != None:
                try:
                    self.secondAxe.remove()
                except:
                    print("O segundo eixo não existe")
            if x_isDate == True:
                self.x_axes_set_date(x)

            # Caso exista mais um tipo de unidade nos dados
            firstUnit = units[0]
            for i in range(1, len(units)):
                if firstUnit != units[i]:
                    print(firstUnit, units[i])
                    self.secondAxe = self.canvas.axes.twinx()
                    ylabel = r"$^oC$" if units[i] == "C" else r"$\mu\epsilon$"
                    self.secondAxe.set_ylabel(ylabel)
                    break
            
            ylabel = r"$^oC$" if firstUnit == "C" else r"$\mu\epsilon$"
            self.canvas.axes.set_ylabel(ylabel)

            lines = []
            for i in range(len(x)):
                if diff == True:
                    y[i] = self.diff(y[i])
                if removeOutliers == True:
                    x[i], y[i] = self.removeOutliers(x[i], y[i])
                if continuity == True:
                    x[i], y[i] = self.continuity(x[i], y[i])
                label = f"Linha {i}" if labels == [] else labels[i]
                if units[i] == firstUnit:
                    line = self.canvas.axes.plot(x[i], y[i], label=label, color=self.colors[i])
                else:
                    line = self.secondAxe.plot(x[i], y[i], label=label, color=self.colors[i])
                lines.append(line[0])

            labs = [l.get_label() for l in lines]
            legend = self.canvas.axes.legend(lines, labs, bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
                                             mode="expand", borderaxespad=0, ncol=4)
            lines_legend = legend.get_lines()
            for i in range(len(lines_legend)):
                lines_legend[i].set_picker(True)
                lines_legend[i].set_pickradius(5)
                self.graphs[lines_legend[i]] = lines[i]

            self.canvas.figure.canvas.mpl_connect("pick_event", self.on_pick)
            self.canvas.draw()
        
    def on_pick(self, event):
        legend = event.artist
        isVisible = legend.get_visible()
        self.graphs[legend].set_visible(not isVisible)
        legend.set_visible(not isVisible)
        y_max, y_min = 0, 0

        op = "Strain" if "Strain" in self.graphs[legend].get_label() else "Temp"
        for key in self.graphs.keys():
            if self.graphs[key].get_visible() and op in self.graphs[key].get_label():
                if y_max < max(self.graphs[key].get_ydata()):
                    y_max = max(self.graphs[key].get_ydata())
                if y_min > min(self.graphs[key].get_ydata()):
                    y_min = min(self.graphs[key].get_ydata())

        op = "epsilon" if "Strain" in op else "C"
        if op in self.canvas.axes.get_ylabel():
            edit = self.canvas.axes
        else:
            edit = self.secondAxe

        if(abs(y_min*1.1 - y_min) > abs(y_max*1.1 - y_max)):
            edit.set_ylim([y_min*1.1, y_max + abs(y_min*1.1 - y_min)])
        else:
            edit.set_ylim([y_min*1.1 - abs(y_max*1.1 - y_max), y_max*1.1])

        self.canvas.draw()