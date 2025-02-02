import nvna
import numpy as np
import matplotlib.pyplot as plt

cal_fname = './nvna_current_cal.csv'

print("connecting to the NanoVNA... ")
instrument = nvna.NVNA(fcal=cal_fname, Tmode=True)
print('connected')

input('Plug through hole Cap and press enter')
instrument.PORT1_measurement()
freq, Z_m_deembed_th1 = instrument.get_last_PORT1_Impedance()

plt.figure()
plt.plot(freq, np.abs(Z_m_deembed_th1),label='traversante')
plt.loglog()
plt.grid()
plt.legend()


del instrument
plt.show()