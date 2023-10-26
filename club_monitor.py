import typing
from PyQt6 import QtGui
from DisplayWindow import DisplayWindow
from instruments import MaxiGaugeInst, get_instrument_class

import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QSize, QTimer

from common import *
import random

display_ids = get_sections_cfg(DISPLAY_CFG_FILE)         # read all displays and their settings
instrument_ids = get_sections_cfg(INSTRUMENT_CFG_FILE)   # read all instruments and theire settings 

instruments = {}                # references to instument objects

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(1920, 1080))
        self.windows = []
        # self.button = QPushButton("Push for Window")
        # self.button.clicked.connect(self.change_label)
        # self.setCentralWidget(self.button)

        
        # match instruments from config flie with proper classes
        for inst in instrument_ids:
            instruments[inst] = get_instrument_class(inst)
        # initiate those instruments
        for inst in instruments:
            instruments[inst] = instruments[inst](inst)     # rewrite class by its newly created instance 

        for idx, disp in enumerate(display_ids):
            inst_id = read_cfg(DISPLAY_CFG_FILE, disp, 'instrument')
            win = DisplayWindow(disp, instruments[inst_id].get_value)
            win.show()
            self.windows.append(win)

            # set timer for reading instruments
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_instruments)
        self.timer.start(100)                              # 1000 milliseconds = 1 second


    def read_instruments(self):
        for inst in instruments:
            instruments[inst].read_values()

        
    def closeEvent(self, event):
        self.timer.stop()


stylesheet = """
    MainWindow {
        background-image: url("club.jpg"); 
        background-repeat: no-repeat; 
        background-position: center;
    }
"""
app = QApplication(sys.argv)
app.setStyleSheet(stylesheet)
w = MainWindow()
w.show()
app.exec()