import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt




fname = './th_cap1.csv'
data = np.loadtxt(fname, dtype=np.complex128, delimiter=',', skiprows=1)

def Z_mod(freq, C, L, R):
    ZC = 1/(1j*C*2*np.pi*freq)
    ZR = R
    ZL = 1j*L*2*np.pi*freq
    return np.abs(ZL + ((ZC * ZR)/(ZC + ZR)))

freq = np.real(data[:, 0])
Z_mesure = data[:, 2]
# restrict frequency

f_max = 1e9
f_min = 1e7


imax = freq.searchsorted(f_max, 'right') - 1
imin = freq.searchsorted(f_min, 'right')
freq = freq[imin:imax]
Z_mesure = Z_mesure[imin:imax]

popt, pcov = opt.curve_fit(Z_mod, freq, np.abs(Z_mesure), p0=[0.1e-9, 1e-9, 1e5])

print(popt)

plt.figure()
plt.plot(freq, np.abs(Z_mesure), label='mesure')
plt.plot(freq, Z_mod(freq, *popt), label='modèle')
plt.loglog()
plt.legend()

plt.show()