from DisplayWindow import diplay_window
from instruments import get_instrument_class

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog
from PyQt5.QtCore import QSize, QTimer, Qt

import common as cmn

instrument_ids = cmn.get_sections_cfg(cmn.INSTRUMENT_CFG_FILE)   # read all instruments and theire settings 

instruments = {}      # dictionary of instument objects instancies (key is instrument id)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(1920, 1080))
        self.move(0, 0)

        self.displays = []
        # self.button = QPushButton("Push for Window")
        # self.button.clicked.connect(self.change_label)
        # self.setCentralWidget(self.button)

        self.init_instruments()
        self.open_displays(cmn.display_cfg_file)
         
            # set timer for reading instruments 
            # note.: not display just read and store, display then get values from inst obj by itself
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_instruments)
        self.timer.start(100)                                  # in miliseconds


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
            win = diplay_window(disp_id, instruments[inst_id])  # pass the reference of the instrument object
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


        """
        Order instruments to aquire - mesure values 
        """    
    def read_instruments(self):
        for inst in instruments:
            instruments[inst].read_values()

        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]
                self.close_displays()
                print("opend diplay: {}".format(file_path))
                self.open_displays(file_path)


        """
        Called when app window is closed
        """
    def closeEvent(self, event):
        self.timer.stop()
        self.close_displays()


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