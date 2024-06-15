from ui_mainwindow import Ui_MainWindow
from PySide6.QtGui import QPixmap
from singleton import singleton

@singleton
class BottleMaps:

    @staticmethod
    def instance():
        return _instance

    def save_map(self):
        main_window = Ui_MainWindow.instance()
        main_window.label_2.setPixmap(QPixmap(u"BottleMaps/maps.jpg"))

_instance = BottleMaps()
