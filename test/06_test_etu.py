import nvna
import numpy as np
import matplotlib.pyplot as plt

print("connecting to the NanoVNA... ")
instrument = nvna.NVNA()
print('connected')
instrument.PORT1_calibration()
print('PORT1 calibrated')


def S2Z(S, z0 = 50.):
    return z0 * ((1+S)/(1-S))


def de_embed(S, Z_short, Z_open, Z_load, z0=50.):
    Z_m = S2Z(S, z0=z0)
    num = z0*(Z_m-Z_short)*(Z_open-Z_load)
    denom = (Z_open-Z_m)*(Z_load-Z_short)
    return num/denom


input('Plug through hole Cap')
freq, S11_m_th1 = instrument.PORT1_measurement()
Z_m_deembed_th1 = de_embed(S11_m_th1, instrument._Z_SHORT, instrument._Z_OPEN, instrument._Z_LOAD)
input('Plug through hole Cap - BAD')
freq, S11_m_th2 = instrument.PORT1_measurement()
Z_m_deembed_th2 = de_embed(S11_m_th2, instrument._Z_SHORT, instrument._Z_OPEN, instrument._Z_LOAD)
input('Plug through SMD')
freq, S11_m_smd1 = instrument.PORT1_measurement()
Z_m_deembed_smd1 = de_embed(S11_m_smd1, instrument._Z_SHORT, instrument._Z_OPEN, instrument._Z_LOAD)
input('Plug through SMD-RF')
freq, S11_m_smd2 = instrument.PORT1_measurement()
Z_m_deembed_smd2 = de_embed(S11_m_smd2, instrument._Z_SHORT, instrument._Z_OPEN, instrument._Z_LOAD)


plt.figure()
plt.plot(freq, np.abs(Z_m_deembed_th1),label='traversante')
plt.plot(freq, np.abs(Z_m_deembed_th2),label='traversante BAD')
plt.plot(freq, np.abs(Z_m_deembed_smd1),label='CMS')
plt.plot(freq, np.abs(Z_m_deembed_smd2),label='CMS-RF')
plt.loglog()
plt.grid()
plt.legend()


del instrument
plt.show()

