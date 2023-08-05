from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
def data(file):
    global file_to_load
    file_to_load = file
import sys

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.seturl(file_to_load)

        self.setCentralWidget(self.browser)

        self.show()
app = QApplication(sys.argv)
window = MainWindow()

app.exec_()