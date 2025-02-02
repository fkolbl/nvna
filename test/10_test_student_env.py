import nvna
import numpy as np
import matplotlib.pyplot as plt

cal_fname = './nvna_current_cal.csv'

def S2Z(S, z0 = 50.):
    return z0 * ((1+S)/(1-S))


def de_embed(S, Z_short, Z_open, Z_load, z0=50.):
    Z_m = S2Z(S, z0=z0)
    num = z0*(Z_m-Z_short)*(Z_open-Z_load)
    denom = (Z_open-Z_m)*(Z_load-Z_short)
    return num/denom

print("connecting to the NanoVNA... ")
instrument = nvna.NVNA(fcal=cal_fname)
print('connected')


input('Plug through hole Cap')
instrument.PORT1_measurement()
freq, Z_m_deembed_th1 = instrument.get_last_PORT1_Impedance()

plt.figure()
plt.plot(freq, np.abs(Z_m_deembed_th1),label='traversante')
plt.loglog()
plt.grid()
plt.legend()


del instrument
plt.show()