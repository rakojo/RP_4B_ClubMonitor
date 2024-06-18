# RP_4B_ClubMonitor

This program is used for reading pressures values from multiple gauge controlers connected
to a single computer and to pressent the values to a common output - screen. 
It is developed primarly for Raspberry PI 4B platform, however is not limited just to it.
Up to now it suppports following controlers:
  - general analog voltage input RP HAT MCC118
  - Pfeffer MaxiGauge
  - XGS600

From user points of view, there are two types of objects and related configuration text files:
- INSTRUMENTS (instruments measuring quantities - pressure)
- DISPLAYS (GUI windows showing measured values)

INSTRUMENTS: "module instruments" and "instruments_config.txt" configuration file
- every type of INSTRUMENT has its controlling class in Instruments module e.g. class "MaxiGaugeInst()"
- the name of class specified in the file should match one of the classes inside the "module instruments"
- the instrument class acquire measured values from an instrument by the "read_values()" method.
- the method is triggered by a timer with a period 'period' parameter specified inside of the "instruments_config.txt" file. 
- the read values are stored in a buffer.
- the instrument class should have "get_value(self, channel)" method, used by the DISPLAY, returning the values from the buffer

DISPLAYS: module DisplayWindow and one of the config file in the "/config" directory
- by the DISPLAYS, the way of showing the values to the screen is meant e.g. window with name and value label or 
  it can be a graph plot 
- the DISPLAY types are represented by its classes in "DisplaWindow" model e.g. "LabelDisplay" or "PlotDisplay"
  inheriting base functionality from the "class Display"
- by timer calling "update_display" method the value is requested from a proper INSTRUMENT class 
  via its "get_value(self, channel)" method