from ui_mainwindow import ui_MainWindow
from PySide6.QtGui import QPixmap
from singleton import singleton

@singleton
class BottleMaps:

    def save_map(self):
        ui_MainWindow.label_2.setPixmap(QPixmap(u"BottleMaps/maps2.jpg"))

bottleMaps = BottleMaps()
