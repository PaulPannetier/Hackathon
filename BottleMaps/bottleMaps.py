import sys
import time
import numpy
from PySide6 import QtCore, QtGui
import PySide6 as Qwt



class BottleMaps:
    

    def save_map(self):
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8("Images/10.jpg")))