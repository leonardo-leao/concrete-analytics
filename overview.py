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
        loadUi("overview.ui", self)
        self.setWindowTitle("Concrete Analytics")
        self.pb_temp_showGif.clicked.connect(lambda: self.showGif("temp"))
        self.progressBar.setMinimum(0)
        self.progressBar.setValue(0)

    def showGif(self, type):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(20)

        # Getting input data from forms
        if type == "temp":
            refDatetime = self.temp_refDatetime.dateTime().toPyDateTime()
            iniDatetime = self.temp_iniDatetime.dateTime().toPyDateTime()
            endDatetime = self.temp_endDatetime.dateTime().toPyDateTime()
        # Getting data from archiver
        dts, vals = [], []
        for s in [2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18, 20]:
            s = f"0{s}" if s < 10 else s
            pvs = arc.get_concrete_pvName(f"TU-{s}*N*Temp")
            x, y, units = anls.dataAvg(None, None, iniDatetime, endDatetime, pvs)
            dts.append(x); vals.append(y)
            self.progressBar.setValue(int(s))

        self.temp_mplOverview.showGif(dts, vals)        



app = QApplication([])
window = ConcreteAnalytics()
window.show()
app.exec_()