from PyQt5 import QtGui

from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QSize

import pyqtgraph as pg

import common as cmn




# =============================================================================
# function DisplayWindow selects proper class to show the display window
# =============================================================================    
def diplay_window(display_id, obj_instrument):
        # type of classes for display windows
    display_types = {'label' : LabelDisplay,
                     'plot' : PlotDisplay}

    type =  str(cmn.read_cfg(cmn.display_cfg_file, display_id, 'type'))

    return display_types[type](display_id, obj_instrument)




# =============================================================================
# Class Display
#
# =============================================================================    

class Display(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, display_id, obj_instrument):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint) # to be on the top above all windows
        self.display_id = display_id                  # string for identification in cfg file 
        self.get_value = obj_instrument.get_value     # reference to function returning values to display
        self.read_config()                            # read position, fond size ... from cfg file
        
        title = self.instrument_id + ' | CH' + str(self.channel)
        self.setWindowTitle(title)
            # set window to be trasparent
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint)      # Remove window frame
        # self.setStyleSheet("background: transparent;")              # Enable a transparent background
        # self.setWindowOpacity(0.2)                                  # Set the window opacity (0.0 to 1.0)

        self.move(self.position[0], self.position[1])
        
        self.create_layout()

            # set timer for calling reading and diplaying function
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)                              # 1000 milliseconds = 1 second


        """
        Creates GUI layout of the diplay window
        """
    def create_layout(self):
        pass


        """
        reads parameters like size and so from the configuretio text file    
        """
    def read_config(self):
        df = cmn.display_cfg_file
        print("Display file name to read config for diplay: {}".format(df))
        self.instrument_id = str(cmn.read_cfg(df, self.display_id, 'instrument id'))
        self.name =          str(cmn.read_cfg(df, self.display_id, 'name'))
        self.channel =       int(cmn.read_cfg(df, self.display_id, 'channel'))
        self.units =         str(cmn.read_cfg(df, self.display_id, 'units'))
        self.position =      tuple(int(x) for x in (cmn.read_cfg(df, self.display_id, 'position').split(',')))
        self.name_size =     int(cmn.read_cfg(df, self.display_id, 'name size'))


    def write_config(self):
        print("Writing to file {} section {}".format(cmn.display_cfg_file, self.display_id))
            # save window position
        cmn.write_cfg(cmn.display_cfg_file, self.display_id, 'position', 
                      str(self.position[0]) + ', ' + str(self.position[1]))


        """
        function run when display window is closed
        """
    def closeEvent(self, event):
        print("Closing {} window !".format(self.name))
        self.write_config()
        self.timer.stop()                                   # stop the timer for display update


        """ 
        when display window is moved update x,y values
        """
    def moveEvent(self, event):
        self.position = (self.pos().x(), self.pos().y())    # update current position

        
        """
        Function reads value from instrument class and displays it in the window
        """    
    def update_display(self):
        pass



  
# =============================================================================
# Class LabelDisplay 
# Shows the values by labet text in the display window 
# =============================================================================    

class LabelDisplay(Display):
    def __init__(self, display_id, obj_instrument):
        super().__init__(display_id, obj_instrument)


        """
        Creates GUI layout of the diplay window
        """
    def create_layout(self):
        layout = QVBoxLayout()

        layout_h = QHBoxLayout()
        self.lbl_name = QLabel(self.name)
        self.lbl_name.setFont(QtGui.QFont("Arial", self.name_size))

        self.lbl_units = QLabel(self.units)
        self.lbl_units.setFont(QtGui.QFont("Arial", self.units_size))

        layout_h.addWidget(self.lbl_name)
        layout_h.addWidget(self.lbl_units)

        self.lbl_value = QLabel("---")
        self.lbl_value.setFont(QtGui.QFont("Arial", self.value_size))
        
        layout.addLayout(layout_h)
        layout.addWidget(self.lbl_value)

        self.setLayout(layout)


        """
        reads parameters like size and so from the configuretio text file    
        """
    def read_config(self):
        super().read_config()
        df = cmn.display_cfg_file
        self.value_size =    int(cmn.read_cfg(df, self.display_id, 'value size'))
        self.units_size =    int(cmn.read_cfg(df, self.display_id, 'units size'))
        self.value_format =  str(cmn.read_cfg(df, self.display_id, 'value format'))


        """
        Function reads value from instrument class and displays it in the window
        """    
    def update_display(self):
        value = format(self.get_value(channel = self.channel), self.value_format)
        self.lbl_value.setText(value)




# =============================================================================
# Class PlotDisplay 
# Shows the values by ploting a chart
# =============================================================================    

class PlotDisplay(Display):
    def __init__(self, display_id, obj_instrument):
        super().__init__(display_id, obj_instrument)
        self.resize(QSize(self.win_size[0], self.win_size[1]))


        """
        Creates GUI layout of the diplay window
        """
    def create_layout(self):
        ## Create some widgets to be placed inside
        self.lbl_value = QLabel('enter text')
        self.plot = pg.PlotWidget()

        ## Create a grid layout to manage the widgets size and position
        layout = QGridLayout()
        self.setLayout(layout)

        ## Add widgets to the layout in their proper positions
        layout.addWidget(self.lbl_value, 0, 0)  # button goes in upper-left
        layout.addWidget(self.plot, 0, 1)  # plot goes on right side, spanning 3 rows

        styles = {'color' : 'red', 'size': self.name_size + 'px'}
        self.plot.setTitle(self.name, **styles)
        styles = {'color':'red', 'font-size': self.axes_size + 'px'}
        self.plot.setLabel('left', 'Pressure {}'.format(self.units), **styles)
        self.plot.setLabel('bottom', 'Measurement no.', **styles)

        self.x = list(range(100))           # 100 time points
        self.y = [0 for ii in range(100)]   # 100 data points = 0 for init

        pen = pg.mkPen(color=(255, 0, 0))
        self.line =  self.plot.plot(self.x, self.y, pen=pen)


        """
        reads parameters like size and so from the configuretio text file    
        """
    def read_config(self):
        super().read_config()
        df = cmn.display_cfg_file
        self.name_size =     str(cmn.read_cfg(df, self.display_id, 'name size'))
        self.axes_size =     str(cmn.read_cfg(df, self.display_id, 'axes label size'))
        self.win_size =      tuple(int(x) for x in (cmn.read_cfg(df, self.display_id, 'size').split(',')))


    def write_config(self):
        super().write_config()
            # save window size
        cmn.write_cfg(cmn.display_cfg_file, self.display_id, 'size', 
                      str(self.win_size[0]) + ', ' + str(self.win_size[1]))

        """
        Function reads value from instrument class and displays it in the window
        """    
    def update_display(self):
        value = self.get_value(channel = self.channel)

        self.x = self.x[1:]             # Remove the first y element.
        self.x.append(self.x[-1] + 1)   # Add a new value 1 higher than the last.

        self.y = self.y[1:]             # Remove the first
        self.y.append( value)  # Add a new value.

        self.line.setData(self.x, self.y)  # Update the data.


        """
        Update current window size
        """    
    def resizeEvent(self, event):
        self.win_size = (self.size().width(), self.size().height())        # update current position
