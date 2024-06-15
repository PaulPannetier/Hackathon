from PySide6.QtUiTools import QUiLoader
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QIODevice, QFile
import sys

if __name__ == '__main__':
    # Some code to obtain the form file name, ui_file_name
    ui_file_name = "ui.ui"
    app = QApplication(sys.argv)
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
        sys.exit(-1)
    loader = QUiLoader()
    widget = loader.load(ui_file, None)
    ui_file.close()
    if not widget:
        print(loader.errorString())
        sys.exit(-1)
    widget.show()
    sys.exit(app.exec_())