import numpy as np
from PfeifferVacuum import MaxiGauge
import common as cmn
  
from PyQt5.QtCore import QTimer

from os.path import exists
from datetime import datetime

# =============================================================================
# Class Buffer to colect instrument read values for averagin
# =============================================================================    
class Buffer():
    def __init__(self, sz):
        self.buffer = np.zeros(sz)
        self.sz = sz
        self.idx = 0    # it is index of cell position for future writing
                        # (idx -1) is the last one which was written to

    def is_full(self):
        return (self.idx >= self.sz)
    
    def clear(self):
        self.buffer.fill(0)
        self.idx = 0

    def insert(self, val):
            # clear automaticly when attend to save more values than buffer size is
        if self.is_full():
            self.clear()
        
        self.buffer[self.idx] = val
        self.idx += 1

    def get_mean(self):
        return self.buffer.mean()

    def get_current(self):
        return self.buffer[self.idx - 1]
    
   
# =============================================================================
# Class MaxiGaugeInst - to comunicate with MaxiGauge instrument
# =============================================================================    

class MaxiGaugeInst():
    def __init__(self, instrument_id):
        self.instrument_id = instrument_id
        self.read_config()

            # list of buffers for colletion of the values before saving them
            # list is used to have the buffer for every channel separately    
        self.buffers = [Buffer(self.average) for x in range(self.num_channels)]    
                                                   
        print("Connecting {}  to {}.".format(self.instrument_id, self.port))
        self.mg = MaxiGauge(self.port)
        self.read_values()
        self.get_value
        print(self.mg.pressures())

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_values)
        self.timer.start(self.period)                     # in miliseconds

    
        """
        read configuration of the instrument from the configuration file
        """
    def read_config(self):
        self.port = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'port'))
        self.type = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'type'))
        self.period = int(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'period'))
        self.average = int(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'save average'))
        self.num_channels = int(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'channels'))
        self.value_format = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'value format'))
        self.dir = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'dir'))


        """
        read values from the MaxiGauge controler and stores them 
        """
    def read_values(self):
        all_channels = self.mg.pressures()
        for buff, channel in zip(self.buffers, all_channels):
            buff.insert(channel.pressure)
                # store the data is 'save average' number reached (= size of buffer)?
                
                # if ch 1 buffer is full => all buffers are full
        if self.buffers[0].is_full():
            self.write_to_file()

        """
        Function is used from outside of class to read stored pressure values 
        """
    def get_value(self, channel):
        return self.buffers[channel-1].get_current()  # -1 because channel 1 needs index 0


    def write_to_file(self):
        dt = datetime.now()
        self.data_file = '{}_{}_{:2}_{}.txt'.format(dt.year, dt.month, dt.day, self.instrument_id)
        
        txt = ''
        if not exists(self.dir + self.data_file):
                # make header of new file
            txt += 'time\t'
            for channel in range(self.num_channels):
                txt += 'CH' + format(channel+1)
                if channel < self.num_channels - 1:
                    txt += '\t'
                else:
                    txt += '\n'
        print(self.dir + self.data_file)
        file=open(self.dir + self.data_file, 'a')

            # make a line with data values
        txt += '{}:{:02}:{:02}\t'.format(dt.hour, dt.minute, dt.second)       # time stamp
        for channel in range(self.num_channels):
            txt += format(self.get_value(channel + 1), self.value_format)
            if channel < self.num_channels - 1: 
                txt += '\t'
            else:
                txt += '\n'
        file.write(txt)
        file.close()

        
        """
        """
    def close(self):
        self.timer.stop()



# =============================================================================
# returning the class of the instrument based on 'type' par. from inst. config file
# =============================================================================    
def get_instrument_class(instrument_id):
    inst_class_name = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, instrument_id, 'type'))
    
    return eval(inst_class_name)    # eval is used to convert str to class
