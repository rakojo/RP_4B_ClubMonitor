from PyQt6 import QtGui
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer

from common import *

# =============================================================================
# Class DisplayWindow
# =============================================================================    

class DisplayWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, display_id, value_function):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint) # to be on the top above all windows
        self.display_id = display_id                           # string for identification in cfg file 
        self.read_config()                                     # read position, fond size ... from cfg file
        self.get_value = value_function                        # reference to function returning values to display
        
        self.setWindowTitle(self.name)
            # set window to be trasparent
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)      # Remove window frame
        # self.setStyleSheet("background: transparent;")              # Enable a transparent background
        # self.setWindowOpacity(0.2)                                  # Set the window opacity (0.0 to 1.0)

        self.move(self.position[0], self.position[1])
        
        layout = QVBoxLayout()

        self.lbl_name = QLabel(self.name)
        self.lbl_name.setFont(QtGui.QFont("Arial", self.name_size))

        self.lbl_value = QLabel("1.15e-9")
        self.lbl_value.setFont(QtGui.QFont("Arial", self.value_size))
        
        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_value)

        self.setLayout(layout)

            # set timer for calling reading and diplaying function
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)                              # 1000 milliseconds = 1 second


    # reads parameters like size and so from the text file    
    def read_config(self):
        df =  DISPLAY_CFG_FILE
        self.name =         str(read_cfg(df, self.display_id, 'name'))
        self.channel =      int(read_cfg(df, self.display_id, 'channel'))
        self.position =     tuple(int(x) for x in (read_cfg(df, self.display_id, 'position').split(',')))
        self.name_size =    int(read_cfg(df, self.display_id, 'name size'))
        self.value_size =   int(read_cfg(df, self.display_id, 'value size'))
        self.value_format = str(read_cfg(df, self.display_id, 'value format'))


    # to run somethig when display window is closed
    def closeEvent(self, event):
        print("Closing {} window !".format(self.name))
            # save window position
        write_cfg(DISPLAY_CFG_FILE, self.display_id, 'position', 
                  str(self.position[0]) + ', ' + str(self.position[1]))
        self.timer.stop()                                   # stop the timer for display update

    # when display window is moved
    def moveEvent(self, event):
        self.position = (self.pos().x(), self.pos().y())    # update current position
        
    def update_display(self):
        print("Running the update function for {} every 1 second".format(self.name))
            # calling of function related to specific instrument responsible for returning measured values
        value = format(self.get_value(channel = self.channel), self.value_format)
        self.lbl_value.setText(value)
