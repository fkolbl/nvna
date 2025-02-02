import nvna
import numpy as np
import matplotlib.pyplot as plt

print("connecting to the NanoVNA... ")
instrument = nvna.NVNA()
print('connected')
instrument.PORT1_calibration()
print('PORT1 calibrated')

del instrument