from PfeifferVacuum import MaxiGauge
import common as cmn
  

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

    
        """
        read configuration of the instrument from the configuration file
        """
    def read_config(self):
        self.port = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'port'))
        self.type = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, self.instrument_id, 'type'))


        """
        read values from the MaxiGauge controler and stores them 
        """
    def read_values(self):
        self.pressures = self.mg.pressures()


        """
        this function is used from outside of class to read stored pressure values 
        """
    def get_value(self, channel):
        return self.pressures[channel-1].pressure       # -1 because channel 1 needs index 0


# =============================================================================
# returning the class of the instrument based on 'type' par. from inst. config file
# =============================================================================    
def get_instrument_class(instrument_id):
    inst_class_name = str(cmn.read_cfg(cmn.INSTRUMENT_CFG_FILE, instrument_id, 'type'))
    
    return eval(inst_class_name)    # eval is used to convert str to class