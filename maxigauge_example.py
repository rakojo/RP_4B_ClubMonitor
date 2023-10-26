#!/usr/bin/env python

### Load the module:
from PfeifferVacuum import MaxiGauge

### Initialize an instance of the MaxiGauge controller with
### the handle of the serial terminal it is connected to
mg = MaxiGauge('COM3')
# mg = MaxiGauge('/dev/ttyUSB0')

### Run the self check (not needed)
print(mg.checkDevice())

### Set device characteristics (here: change the display contrast)
print("Set the display contrast to: %d" % mg.displayContrast(10))
### Read out the pressure gauges
print(mg.pressures())

### Display the value of the pressure gauges for 20 repeated read outs
for i in range(20):
    ps = mg.pressures()
    for channel in range(5):
        print("Sensor {}: {} mbar \n".format(ps, ps[channel].pressure))