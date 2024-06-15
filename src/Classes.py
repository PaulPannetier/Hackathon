from PyQt5.QtCore import pyqtSignal,QRect,Qt,QSize,QPoint
from PyQt5.QtWidgets import QTableWidgetItem,QTableWidget,QWidget,QStyle,QToolButton,QPushButton,QHBoxLayout,QLineEdit,QDialog,QComboBox,QLabel,QDesktopWidget
from PyQt5.QtGui import QIcon,QFont,QPixmap,QPainter,QPen,QColor
import os

class Drawing(QWidget):
    """dessine les axes et les participants"""
    def __init__(self,menu):
        super().__init__(menu.home)
        self.menu=menu
        self.pix=(QPixmap(os.path.dirname(__file__) + "/pictures/axes.png")).scaledToHeight(800)
        self.image=QLabel(self)
        self.image.setStyleSheet("background-color: {};border: 1px solid;border-color: #dadfe5;".format(self.menu.backgroundColor))
        self.image.setGeometry(QRect(0,0,self.pix.width(),self.pix.height()))
        self.image.setPixmap(self.pix)