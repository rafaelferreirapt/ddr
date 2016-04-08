import numpy as np
import matplotlib.pyplot as plt
import sys
import json
from scipy.optimize import curve_fit

plt.ion()
data1 = np.loadtxt('../dataFiles/data1')


def waitforEnter():
    if sys.version_info[0] == 2:
        raw_input("Press ENTER to continue.")
    else:
        input("Press ENTER to continue.")

# -18- #
x = data1[:, 2]
M = np.mean(x)
V = np.var(x)
H, bins = np.histogram(x, bins=20)
probs = 1.0 * H / np.sum(H)

# Exponential
ye = np.random.exponential(M, (300, 20))
# Gaussian/Normal
yg = np.random.normal(M, V ** 0.5, (300, 20))
# Empirical discrete
yd = np.random.choice(bins[:-1], (300, 20), p=probs)

# -20- #

with open('../dataFiles/ams-ix-traffic.json') as data_file:
    data = json.load(data_file)
Xout = []
for monthT in data:
    Xout.append(monthT['out_traffic'])


def linearG(t, Y0, R):
    return Y0 + R * t


def expG(t, Y0, A0, R):
    return Y0 + A0 * np.exp(R * t)


t = np.arange(0, len(Xout))
paramsL, cov = curve_fit(linearG, t, Xout)
paramsE, cov = curve_fit(expG, t, Xout, [500, 1, .01])
plt.figure(17)
plt.plot(t, Xout, 'k')
plt.plot(t, linearG(t, paramsL[0], paramsL[1]), 'b')
plt.plot(t, expG(t, paramsE[0], paramsE[1], paramsE[2]), 'r')
plt.show()

# End
waitforEnter()
