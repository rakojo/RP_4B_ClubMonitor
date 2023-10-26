from PfeifferVacuum import MaxiGauge
from common import *
  

# =============================================================================
# Class MaxiGaugeInst - to comunicate with MaxiGauge instrument
# =============================================================================    

class MaxiGaugeInst():
    def __init__(self, instrument_id):
        self.instrument_id = instrument_id
        self.read_config()

        print("Connecting {}  to {}.".format(self.instrument_id, self.port))
        self.mg = MaxiGauge(self.port)
        self.read_values()
        print(self.pressures)

    def read_config(self):
        self.port = str(read_cfg(INSTRUMENT_CFG_FILE, self.instrument_id, 'port'))
        self.type = str(read_cfg(INSTRUMENT_CFG_FILE, self.instrument_id, 'type'))

    def read_values(self):
        self.pressures = self.mg.pressures()

    def get_value(self, channel):
        return self.pressures[channel-1].pressure       # -1 because channel 1 needs index 0




    # dict for matching config file names of instruments with classes
instrument_class = {'MaxiGauge' : MaxiGaugeInst}

    # returning class of the instrument based on type string from inst. config file
def get_instrument_class(instrument_id):
    type_id = str(read_cfg(INSTRUMENT_CFG_FILE, instrument_id, 'type'))
    
    return instrument_class[type_id]