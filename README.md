# RP_4B_ClubMonitor

There are two types of objects and related config txt files :

- INSTRUMENTS (contains instruments measuring quantities - pressure)
- DISPLAYS (windows showing values measured by dyspaly)

INSTRUMENTS : module Instruments and instruments_config.txt configuration file

- every INSTRUMENT has its controling class in Instruments module e.g. class "MaxiGaugeInst()"
- the name of class specified in the cfg. file should match one of the classes inside the inst. module
- the class aquire mmeasured values from instrument by "read_values()" function.
  The func. is trigered by a timer with a period 'period' parameter from inst. cfg. file. 
  Readed values are stored in the buffer.
- the class should have "get_value(self, channel)" fuction returnig the values from the buffer to a DISPLAY

DISPLAYS: module DisplayWindow and one of the config file in "/displays_cfgs" directory"

- by the DISPLAYS, the way of showing the values to the screen is meant e.g. window with name and value label or 
  it can be a graph plot 
- the DISPLAY types are represented by ist clasess in "DisplaWindow" model e.g. "LabelDisplay" or "PlotDisplay"
  inheritig base functionality from the "class Display"
- by timer caling "update_display" function value is requsted from a proper INSTRUMENT class 
  by the its "get_value(self, channel)" fuction and show it in DISPLAY window
