from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from archiver import Archiver as arc

class SelectPvs(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("selectPvs.ui", self)
        self.setWindowTitle("Select PVs")
        self.pb_selectAll.clicked.connect(lambda: self.selectAllPvs(True))
        self.pb_deselectAll.clicked.connect(lambda: self.selectAllPvs(False))
        self.pb_load.clicked.connect(self.load)
        self.progressBar.setMinimum(0)
        self.pvs = []
        self.xData = []
        self.yData = []
        self.units = []

        self.ini = None
        self.end = None
        self.plot = None
        self.log = None

    def selectPvs(self, pvs, ini, end, log):
        layout = self.verticalLayout
        self.progressBar.setValue(0)
        self.ini = ini
        self.end = end
        self.log = log
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)
        for i in range(len(pvs)):
            layout.addWidget(QCheckBox(pvs[i]))
        layout.setAlignment(Qt.AlignTop)

    def selectAllPvs(self, op: bool):
        layout = self.verticalLayout
        for i in range(layout.count()):
            layout.itemAt(i).widget().setChecked(op)

    def load(self):
        pvs = []
        layout = self.verticalLayout
        for i in range(layout.count()):
            if layout.itemAt(i).widget().isChecked():
                pvs.append(layout.itemAt(i).widget().text())

        self.progressBar.setMaximum(len(pvs))

        x, y, units = [], [], []
        iniDatetime = arc.datetimeToStr(self.ini)
        endDatetime = arc.datetimeToStr(self.end)
        for i in range(len(pvs)):
            dt, val, unit = arc.pv_request(pvs[i], iniDatetime, endDatetime)
            x.append(dt); y.append(val); units.append(unit)
            self.progressBar.setValue(i+1)

        self.xData = x
        self.yData = y
        self.units = units
        self.pvs = pvs

        self.log.append("<p style='color: green'>Successfully obtained PVs!</p>")

        self.close()