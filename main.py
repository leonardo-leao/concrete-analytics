from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from mapa import Mapa
from analysis import Analysis as anls
from selectpvs import SelectPvs
from archiver import Archiver as arc

class ConcreteAnalytics(QMainWindow):
    
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("interface.ui", self)
        self.setWindowTitle("Concrete Analytics")
        self.addToolBar(NavigationToolbar(self.matplotlibWidget.canvas, self))
        self.searchButton.clicked.connect(self.search_pv)
        self.plotButton.clicked.connect(self.plot)
        self.progressBarPlot.setMinimum(0)
        self.progressBarPlot.setValue(0)

        self.iniDatetime = None
        self.endDatetime = None

        # Save the last temperature average that was loaded
        self.rangeDate_tempAvg = []
        self.x_tempAvg = []
        self.y_tempAvg = []

        # Menu Buttons
        self.menuSensors = Mapa()
        self.pb_menu_sensors.clicked.connect(self.open_sensors)

        self.selectPvs = SelectPvs()

    def open_sensors(self):
        self.menuSensors.show()

    def plot(self, x: list = [], y: list = []):
        self.progressBarPlot.setValue(0)
        x = self.selectPvs.xData.copy()
        y = self.selectPvs.yData.copy()
        pvs = self.selectPvs.pvs.copy()
        units = self.selectPvs.units.copy()
        labels = pvs.copy()

        if self.iniDatetime == None or self.endDatetime == None:
            self.iniDatetime = self.form_iniDatetime.dateTime().toPyDateTime()
            self.endDatetime = self.form_endDatetime.dateTime().toPyDateTime()

        if self.cb_addTempAverage.isChecked():
            self.log_insertMsg("Generating temperature average, this might take a few minutes...")
            if (self.x_tempAvg == [] or self.y_tempAvg == [] or self.rangeDate_tempAvg == []):
                if self.rangeDate_tempAvg != [self.iniDatetime, self.endDatetime]:
                    self.x_tempAvg, self.y_tempAvg, unit_tempAvg = anls.dataAvg(self.progressBarPlot, 0.9, self.iniDatetime, self.endDatetime, arc.get_concrete_pvName("TU*Temp"))
                    self.rangeDate_tempAvg = [self.iniDatetime, self.endDatetime]
            x.append(self.x_tempAvg)
            y.append(self.y_tempAvg)
            units.append(unit_tempAvg)
            labels.append("Concrete Temperature Average")

        if (x != [] and y != [] and labels != [] and units != []):

            if self.cb_average.isChecked():
                x_avg, y_avg, units_avg = anls.dataAvg(self.progressBarPlot, 0.9, self.iniDatetime, self.endDatetime, pvs)
                x.append(x_avg)
                y.append(y_avg)
                units.append(units_avg)
                labels.append("Data Average")

            self.matplotlibWidget.plot(x, y, labels=labels, units=units, 
                diff = self.cb_setDiff.isChecked(), 
                removeOutliers = self.cb_removeOutliers.isChecked(), 
                continuity = self.cb_forceContinuity.isChecked(),
                x_isDate = True)
        else:
            self.log_insertMsg("Pvs was not loaded...")

    def search_pv(self):
        pvName = self.pvName.text()

        self.iniDatetime = self.form_iniDatetime.dateTime().toPyDateTime()
        self.endDatetime = self.form_endDatetime.dateTime().toPyDateTime()

        if pvName != "" and self.iniDatetime != self.endDatetime:
            pv = arc.get_concrete_pvName(pvName)
            self.selectPvs.selectPvs(pv, self.iniDatetime, self.endDatetime, self.logBox)
            self.selectPvs.show()
        else:
            self.log_insertMsg("Complete all the fields correctly...")

    def log_insertMsg(self, message):
        self.logBox.append(message)


app = QApplication([])
window = ConcreteAnalytics()
window.show()
app.exec_()