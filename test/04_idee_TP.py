import nvna
import numpy as np
import matplotlib.pyplot as plt


#### fonctions
def S2Z(S, z0 = 50.):
    return z0 * ((1+S)/(1-S))

####
f_start = 5e4   # in Hz
f_stop = 3e9    # in Hz
n_points = 201

print("connecting to the NanoVNA... ")
instrument = nvna.NVNA()

### mesure 

freq, S11 = instrument.get_S11(f_start, f_stop, n_points)

Z_m = S2Z(S11)

plt.figure()
plt.plot(freq, np.abs(Z_m))
plt.loglog()

C_guess = 1e9/(np.abs(Z_m[0])*2*np.pi*freq[0])
print("C guessed from measurement = %f nF" % C_guess)

plt.show()



del(instrument)