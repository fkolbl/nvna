import nvna

f_start = 5e4   # in Hz
f_stop = 1.7e9    # in Hz

print("connecting to the NanoVNA... ")
test = nvna.NVNA()
print("\t connection done")
test.set_sweep(f_start, f_stop)
print("\t changed sweep frequency")

del(test)
print("NVNA disconnected")
