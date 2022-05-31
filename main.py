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
        x = self.selectPvs.xData.copy()
        y = self.selectPvs.yData.copy()
        pvs = self.selectPvs.pvs.copy()
        units = self.selectPvs.units.copy()

        if self.iniDatetime == None or self.endDatetime == None:
            self.iniDatetime = self.form_iniDatetime.dateTime().toPyDateTime()
            self.endDatetime = self.form_endDatetime.dateTime().toPyDateTime()

        if self.cb_addTempAverage.isChecked():
            if (self.x_tempAvg == [] or self.y_tempAvg == [] or self.rangeDate_tempAvg == []):
                if self.rangeDate_tempAvg != [self.iniDatetime, self.endDatetime]:
                    self.log_insertMsg("Generating temperature average, this might take a few minutes...")
                    self.x_tempAvg, self.y_tempAvg = anls.temperatureAvg(self.iniDatetime, self.endDatetime)
                    self.rangeDate_tempAvg = [self.iniDatetime, self.endDatetime]
            unit_tempAvg = ["C" for _ in range(len(self.x_tempAvg))]
            x.append(self.x_tempAvg)
            y.append(self.y_tempAvg)
            units.append(unit_tempAvg)
            pvs.append("Concrete Temperature Average")
        else:
            self.log_insertMsg("Nothing to plot...")

        if (x != [] and y != [] and pvs != [] and units != []):
            self.matplotlibWidget.plot(x, y,labels=pvs, units=units, 
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