import nvna
import numpy as np
import matplotlib.pyplot as plt

f_start = 5e4   # in Hz
f_stop = 6.3e9    # in Hz
n_points = 501

print("connecting to the NanoVNA... ")
test = nvna.NVNA()
print("\t connection done")
test.set_sweep(f_start, f_stop, n_points)
print("\t changed sweep frequency")

#freq = test.get_frequencies()
#print(freq)

#freq, S11, S21 = test.get_S_parameters(f_start, f_stop, n_points)
freq, S11 = test.get_S11(f_start, f_stop, n_points)

del(test)
print("NVNA disconnected")

plt.figure()
plt.plot(freq, np.abs(S11), label='S11')
#plt.plot(freq, np.abs(S21), label='S21')
plt.semilogy()
plt.legend()

plt.show()

