import numpy as np
import matplotlib.pyplot as plt
import sys
import json
from scipy.optimize import curve_fit

plt.ion()
data1 = np.loadtxt('../dataFiles/data1')

# sudo pip install --upgrade numpy


def waitforEnter():
    if sys.version_info[0] == 2:
        raw_input("Press ENTER to continue.")
    else:
        input("Press ENTER to continue.")

# -18- #
num_columns = 1

x = data1[:, 2]
M = np.mean(x)
V = np.var(x)
H, bins = np.histogram(x, bins=20)
probs = 1.0 * H / np.sum(H)

# Exponential
ye = np.random.exponential(M, (300, num_columns))
# Gaussian/Normal
yg = np.random.normal(M, V ** 0.5, (300, num_columns))
# Empirical discrete
yd = np.random.choice(bins[:-1], (300, num_columns), p=probs)

t = np.arange(0, len(ye))
plt.figure(16)
plt.plot(t, x, 'k', label="original")
plt.plot(t, ye, 'b', label="exp")
plt.plot(t, yg, 'g', label="gaus")
plt.plot(t, yd, 'r', label="discrete")
plt.legend()
plt.show()
plt.savefig("../imagens/distribution/ex18.png")

# waitforEnter()

# -19- #
x = data1[:, 2]
threshold = 1
idx = (x > threshold)
value_true = x[idx]
value_false = x[np.logical_not(idx)]
true_mean = np.mean(value_true)
false_mean = np.mean(value_false)

print true_mean
print false_mean

duration_on = []
duration_off = []

counter = 1

for i in range(0, len(idx)-1):
    if idx[i] != idx[i+1]:
        if idx[i]:
            duration_on.append(counter)
        else:
            duration_off.append(counter)
        counter = 1
    else:
        counter += 1

print np.mean(duration_off)
print np.mean(duration_on)

mean_duration_on = np.mean(duration_on)
mean_duration_off = np.mean(duration_off)

# true_mean = lambda

out = np.zeros(400)

k = 0

while k < 300:
    rdm_on = np.max([1, int(np.random.exponential(mean_duration_on, 1)[0])])
    out[k:k+rdm_on] = np.random.exponential(true_mean, rdm_on)
    k += rdm_on+1
    rdm_off = np.max([1, int(np.random.exponential(mean_duration_off, 1)[0])])
    k += rdm_off+1

out = out[:300]

plt.figure(18)
plt.plot(t, x, 'k', label="original")
plt.plot(t, out, 'b', label="generated")
plt.legend()
plt.show()
plt.savefig("../imagens/distribution/ex19.png")

# waitforEnter()
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
t = np.arange(0, int(len(Xout)+len(Xout)*0.2))
plt.plot(t, linearG(t, paramsL[0], paramsL[1]), 'b')
plt.plot(t, expG(t, paramsE[0], paramsE[1], paramsE[2]), 'r')
plt.show()
plt.savefig("../imagens/distribution/ex20.png")

# End
waitforEnter()
