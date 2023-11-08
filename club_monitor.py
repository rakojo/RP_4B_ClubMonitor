# There are two types of objects and related config txt files :
#                - INSTRUMENTS (contains instruments measuring quantities - pressure)
#                - DISPLAYS (windows showing values measured by dyspaly)
#
# INSTRUMENTS : module Instruments and instruments_config.txt configuration file
# - every INSTRUMENT has its controling class in Instruments module e.g. class "MaxiGaugeInst()"
# - the name of class specified in the cfg. file should match one of the classes inside the inst. module
# - the class aquire mmeasured values from instrument by "read_values()" function.
#   The func. is trigered by a timer with a period 'period' parameter from inst. cfg. file. 
#   Readed values are stored in the buffer.
# - the class should have "get_value(self, channel)" fuction returnig the values from the buffer to a DISPLAY
#
# DISPLAYS: module DisplayWindow and one of the config file in "/displays_cfgs" directory"
# - by the DISPLAYS, the way of showing the values to the screen is meant e.g. window with name and value label or 
#   it can be a graph plot 
# - the DISPLAY types are represented by ist clasess in "DisplaWindow" model e.g. "LabelDisplay" or "PlotDisplay"
#   inheritig base functionality from the "class Display"
# - by timer caling "update_display" function value is requsted from a proper INSTRUMENT class 
#   by the its "get_value(self, channel)" fuction and show it in DISPLAY window


from DisplayWindow import diplay_window
from instruments import get_instrument_class

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtCore import QSize, QTimer, Qt, QEvent
from PyQt5.QtGui import QIcon

import common as cmn

instrument_ids = cmn.get_sections_cfg(cmn.INSTRUMENT_CFG_FILE)   # read all instruments and theire settings 

instruments = {}      # dictionary of instument objects instancies (key is instrument id)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(QSize(1920, 1080))
        self.move(0, 0)

        self.displays = []

        self.init_instruments()
        self.open_displays(cmn.display_cfg_file)

        self.title_on = False

        """
        Get proper classes for instruments in configuration file and create instances
        This will innitiate connection to the instrument by the class constructor
        """
    def init_instruments(self):
            # get instrument's class from config file
        for inst_id in instrument_ids:
            instruments[inst_id] = get_instrument_class(inst_id)
  
            # initiate those class instruments - get instance
        for inst_id in instruments:
            instruments[inst_id] = instruments[inst_id](inst_id)        # replace class name by its newly created
                                                                        # instance 


        """
        Open all the displays specified in the configuration txt file 'cfg_file'
        """
    def open_displays(self, cfg_file):
        display_ids = cmn.get_sections_cfg(cfg_file)      # read all displays settings
        cmn.display_cfg_file = cfg_file
        
        for disp_id in display_ids:
            inst_id = cmn.read_cfg(cfg_file, disp_id,     # get instrument id of the display
                                   'instrument id')  
            win = diplay_window(self, disp_id, instruments[inst_id])  # pass the reference of the instrument object
                                                                      # to a display class init and show its window
            win.show()
            self.displays.append(win)


        """
        Close all the opened displays and clear list with the references
        """
    def close_displays(self):
        for win in self.displays:
            win.close()
        
        self.displays.clear()      # claer list with all the references to display objects


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.title_on = False
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                self.close_displays()
                cmn.verbose("Opend diplay config. file: {}".format(file_path))
                self.open_displays(file_path)

        if event.key() == Qt.Key_F1:
            self.title_on = False
            file_path = cmn.DIR_CFG +'displays_config_F1.txt'
            self.close_displays()
            cmn.verbose("Opend diplay config. file: {}".format(file_path))
            self.open_displays(file_path)

        if event.key() == Qt.Key_F2:
            self.title_on = False
            file_path = cmn.DIR_CFG + 'displays_config_F2.txt'
            self.close_displays()
            cmn.verbose("Opend diplay config. file: {}".format(file_path))
            self.open_displays(file_path)

        if event.key() == Qt.Key_F3:
            self.title_on = False
            file_path = cmn.DIR_CFG + 'displays_config_F3.txt'
            self.close_displays()
            cmn.verbose("Opend diplay config. file: {}".format(file_path))
            self.open_displays(file_path)

        if event.key() == Qt.Key_F4:
            self.title_on = False
            file_path = cmn.DIR_CFG + 'displays_config_F4.txt'
            self.close_displays()
            cmn.verbose("Opend diplay config. file: {}".format(file_path))
            self.open_displays(file_path)

        if event.key() == Qt.Key_F10:
            if not self.title_on:
                flag = Qt.WindowTitleHint | Qt.WindowCloseButtonHint |  Qt.WindowType.WindowStaysOnTopHint | Qt.Tool # show win. title bar
                      
            else:
                flag = Qt.FramelessWindowHint |  Qt.WindowType.WindowStaysOnTopHint | Qt.Tool # hide win. title bar

            for win in self.displays:
                win.setWindowFlags(flag)                        
                win.show()

            self.title_on = not self.title_on     # toggle  


        """Called when app window is minimalized, maximalized
        """
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if event.oldState() and Qt.WindowMinimized:
                for win in self.displays:
                    win.setWindowState(Qt.WindowActive)
            elif event.oldState() == Qt.WindowNoState or self.windowState() == Qt.WindowMaximized:
                for win in self.displays:
                    win.setWindowState(Qt.WindowMinimized)


        """
        Called when app window is closed
        """
    def closeEvent(self, event):
        self.close_displays()
            # close all instruments
        for inst in instruments:
            instruments[inst].close()


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
