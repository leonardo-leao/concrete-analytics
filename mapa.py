from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Mapa(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("mapa.ui", self)
        self.setWindowTitle("Sensors Map")

app = QApplication([])
window = Mapa()
window.show()
app.exec_()