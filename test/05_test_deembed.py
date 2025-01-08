import nvna
import numpy as np
import matplotlib.pyplot as plt

####
f_start = 5e4   # in Hz
f_stop = 3e9    # in Hz
n_points = 201

print("connecting to the NanoVNA... ")
instrument = nvna.NVNA()


#### fonctions
def S2Z(S, z0 = 50.):
    return z0 * ((1+S)/(1-S))

def de_embed(S, Z_open, Z_short, Z_load, z0=50):
    Z_m = S2Z(S)
    num = z0*(Z_m-Z_short)*(Z_open-Z_load)
    denom = (Z_open-Z_m)*(Z_load-Z_short)
    return num/denom

def perform_calibration():
    input('plug Open')
    freq, S11_open = instrument.get_S11(f_start, f_stop, n_points)
    input('plug Short')
    _, S11_short = instrument.get_S11(f_start, f_stop, n_points)
    input('plug 50Ohms')
    _, S11_50 = instrument.get_S11(f_start, f_stop, n_points)
    return freq, S2Z(S11_open), S2Z(S11_short), S2Z(S11_50)

if __name__ == '__main__':
    print('--------------------------')
    print('First Perform calibrations')
    print('--------------------------')
    freq, Z_open, Z_short, Z_50 = perform_calibration()
    
    input('plug measurement Load')
    freq, S11_m = instrument.get_S11(f_start, f_stop, n_points)
    Z_m_deembed = de_embed(S11_m, Z_open, Z_short, Z_50)
    
    
    plt.figure()
    plt.plot(freq, np.abs(Z_open), label='Open')
    plt.plot(freq, np.abs(Z_short), label='Short')
    plt.plot(freq, np.abs(Z_50), label='50Ohms')
    plt.loglog()
    plt.legend()
    
    plt.figure()
    plt.plot(freq, np.abs(Z_m_deembed),label='capa')
    plt.loglog()
    plt.legend()
    
    plt.show()
