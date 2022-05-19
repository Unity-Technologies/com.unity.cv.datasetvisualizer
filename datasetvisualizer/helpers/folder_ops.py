import platform
import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QFileDialog

# General setup
if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()


dialog = QFileDialog()
dialog.setFileMode(QFileDialog.Directory)
dialog.setWindowState(
    dialog.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive
)

if platform.system() == "Windows":
    dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
    dialog.show()

if dialog.exec():
    fileName = dialog.selectedFiles()
    print(fileName[0])
