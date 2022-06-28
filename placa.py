from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from archiver import Archiver as arc
from datetime import datetime, timedelta

class Placa(QMainWindow):

    def __init__(self, sector):
        QMainWindow.__init__(self)
        loadUi("placa.ui", self)
        self.setWindowTitle("Sensors Board")

        self.sector.setText(f"Sector {sector}")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.updateTable(sector)

    def updateTable(self, sector):
        pvs = arc.get_concrete_pvName(f"TU*{sector}S")
        for i in range(len(pvs)):
            rowPosition = self.table.rowCount()
            self.table.insertRow(rowPosition)
            values = pvs[i].split("-")
            if len(values[3]) >= 2:
                self.updateStatus(rowPosition, values[3][0], pvs[i])
                self.table.setItem(rowPosition , 0, QTableWidgetItem(values[3][0]))
                self.table.setItem(rowPosition , 1, QTableWidgetItem(values[3][1]))

            values[3] = values[3].split(":")
            if len(values[3][0]) == 3:
                if values[3][0][2] == "N":
                    self.table.setItem(rowPosition , 2, QTableWidgetItem("NTC"))
                elif values[3][0][2] == "P":
                    self.table.setItem(rowPosition , 2, QTableWidgetItem("PT100"))
                else:
                    self.table.setItem(rowPosition , 2, QTableWidgetItem("VWTS6000"))
            else:
                if "Strain" in values[3][1]:
                    self.table.setItem(rowPosition , 2, QTableWidgetItem("VWS2100"))
                else:
                    self.table.setItem(rowPosition , 2, QTableWidgetItem("-"))

    def updateStatus(self, rowPosition, boardPosition, pv):
        dt, val, _ = arc.pv_request(pv, None, None)
        delta = datetime.now() - dt[-1]

        if val[-1] == 0:
            status = "Offline"
            color = "#FF0000"
        elif delta >= timedelta(hours=2):
            status = "Attention"
            color = "#FFFF00"
        else:
            status = "Online"
            color = "#39FF14"

        if delta >= timedelta(hours=24):
            lastAquisition = dt[-1].strftime('%b-%d, %Y')
        else:
            lastAquisition = dt[-1].strftime('%H:%m')

        if boardPosition == "1":
            self.p1.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "2":
            self.p2.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "3":
            self.p3.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "4":
            self.p4.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "5":
            self.p5.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "6":
            self.p6.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "7":
            self.p7.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "8":
            self.p8.setStyleSheet(f"background-color: {color}")
        elif boardPosition == "9":
            self.p9.setStyleSheet(f"background-color: {color}")

        self.table.setItem(rowPosition , 3, QTableWidgetItem(status))
        self.table.setItem(rowPosition , 4, QTableWidgetItem(lastAquisition))

app = QApplication([])
window = Placa("03")
window.show()
app.exec_()