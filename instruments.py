import numpy as np

from PfeifferVacuum import MaxiGauge
from xgs600 import XGS600Driver

import common as cmn
  
from PyQt5.QtCore import QTimer

from os.path import exists
from os import remove as remove_file
from datetime import datetime

from daqhats import mcc118, OptionFlags, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, chan_list_to_mask




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
# Class Inst - general class to comunicate with instruments instrument
#
#
#  =============================================================================    

class Inst():
    def __init__(self, instrument_id):
        self.instrument_id = instrument_id
        self.read_config()

            # list of buffers for colletion of the values before saving them
            # list is used to have the buffer for every channel separately    
        self.buffers = [Buffer(self.average) for x in range(self.num_channels)]    
                                                   
        cmn.verbose("Connecting {}  to {}.".format(self.instrument_id, self.port))

        self.new_header = True    # to make new header for log file whenever the instance is created - program re-run
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
        self.ch_names = tuple(str(x) for x in (cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE,
                                               self.instrument_id, 'channels names').split(',')))
        self.value_format = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'value format'))
        self.dir = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'dir'))


        """
        Function is used from outside of class to read stored pressure values 
        """
    def get_value(self, channel):
        return self.buffers[channel-1].get_current()  # -1 because channel 1 needs index 0


    def write_to_file(self):
        dt = datetime.now()
        self.data_file = '{}_{:02}_{:02}_{}.txt'.format(dt.year, dt.month, dt.day, self.instrument_id)
        
        txt = ''
            # is it next day or just new program start? - make new header
        if not exists(self.dir + self.data_file) or self.new_header:
            self.new_header = False     # make new header when program starts only ones
                # make header of new file or if this is first execution after program run
            txt += '#time\t'            # every header strarts by #-character
            for channel in range(self.num_channels):
                txt += 'CH' + format(channel+1) + ' : ' + self.ch_names[channel]
                if channel < self.num_channels - 1:
                    txt += '\t'
                else:
                    txt += '\n'
        cmn.verbose(self.dir + self.data_file)
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

            # delete 1 year old file if it exists
        old_file = '{}_{:02}_{:02}_{}.txt'.format(dt.year-1, dt.month, dt.day, self.instrument_id)
        if exists(self.dir + old_file):
            remove_file(self.dir + old_file)
            
        """
        """
    def close(self):
        self.timer.stop()



# =============================================================================
# Class MaxiGaugeInst - to comunicate with MaxiGauge instrument
# =============================================================================    

class MaxiGaugeInst(Inst):
    def __init__(self, instrument_id):
        super().__init__(instrument_id)

        self.mg = MaxiGauge(self.port)
        self.read_values()
        

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


# =============================================================================
# Class XGS600Inst - to comunicate with XGS600 instrument
# =============================================================================    

class XGS600Inst(Inst):
    def __init__(self, instrument_id):
        super().__init__(instrument_id)

        self.xgs = XGS600Driver(self.port)
        self.read_values()

        """
        read values from the XGS600Inst controler and stores them 
        """
    def read_values(self):
        all_channels = self.xgs.read_all_pressures()
        for buff, channel in zip(self.buffers, all_channels):
            buff.insert(channel)

                # store the data is 'save average' number reached (= size of buffer)?
                # if ch 1 buffer is full => all buffers are full
        if self.buffers[0].is_full():
            self.write_to_file()


        
# =============================================================================
# Class MCC118 - to comunicate with ADC HAT of RP (Raspery Pi 8 channel ADC)
# =============================================================================    
# Install library to RP to be able to work !
# ********************************
# Installing and Using the Library
# ********************************

# The project is hosted at https://github.com/mccdaq/daqhats.

# Installation
# ************

# 1. Power off the Raspberry Pi then attach one or more HAT boards (see :ref:`install`).
# 2. Power on the Pi and log in.  Open a terminal window if using the graphical interface.
# 3. Update your package list::

    # sudo apt update
    
# 4. **Optional:** Update your installed packages and reboot::
   
    # sudo apt full-upgrade
    # sudo reboot
    
# 5. Install git (if not installed)::

    # sudo apt install git
    
# 6. Download this package to your user folder with git::

    # cd ~
    # git clone https://github.com/mccdaq/daqhats.git
    
# 7. Build and install the shared library and optional Python support.  The installer will ask if you want to install Python 2 and Python 3 support.  It will also detect the HAT board EEPROMs and save the contents if needed::

    # cd ~/daqhats
    # sudo ./install.sh

class MCC118Inst(Inst):
    def __init__(self, instrument_id):
        super().__init__(instrument_id)

        self.channels = [0, 1, 2, 3, 4, 5, 6, 7]
        self.channel_mask = chan_list_to_mask(self.channels)
        self.num_channels = len(self.channels)

        self.samples_per_channel = 100
        self.scan_rate = 1000.0
        self.options = OptionFlags.DEFAULT

        address = select_hat_device(HatIDs.MCC_118)
        self.hat = mcc118(address)

        self.read_values()


    def read_config(self):

        super().read_config()
        self.expression = tuple(str(x) for x in (cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE,
                                self.instrument_id, 'expression').split(',')))


        """
        read values from the ADC_mcc118 controler and stores them 
        """
    def read_values(self):
        # Read a single value from each selected channel.
        all_channels = []
        self.hat.a_in_scan_start(self.channel_mask, self.samples_per_channel, self.scan_rate,
                                 self.options)

        timeout = 5
        read_request_size = 800
        read_result = self.hat.a_in_scan_read(read_request_size, timeout)

        data = np.array(read_result.data)

        for chan in range(8):
                # average to get single value and get rid of tooth signal noise 
                # of the analog output of the pressure gauge
            x = np.average(data[chan::self.num_channels])
                #recalculate voltage to pressure by expression from inst. cfg. file
            val = eval(self.expression[chan])    # use string expression to evaluate
            all_channels.append(val)

        self.hat.a_in_scan_cleanup()

        for buff, channel in zip(self.buffers, all_channels):
            buff.insert(channel)

                # store the data is 'save average' number reached (= size of buffer)?
                # if ch 1 buffer is full => all buffers are full
        if self.buffers[0].is_full():
            self.write_to_file()


# =============================================================================
# returning the class of the instrument based on 'type' par. from inst. config file
# =============================================================================    
def get_instrument_class(instrument_id):
    inst_class_name = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, instrument_id, 'type'))
    
    return eval(inst_class_name)    # eval is used to convert str to class
