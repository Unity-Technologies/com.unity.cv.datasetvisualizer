import sys
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QFileDialog, QWidget
import platform

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

dialog = QFileDialog()
dialog.setFileMode(QFileDialog.Directory)
dialog.setWindowState(dialog.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)

if (platform.system() == "Windows"):
    dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    dialog.show()

if dialog.exec_():
    fileName = dialog.selectedFiles()
    print(fileName[0])