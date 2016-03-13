import numpy as np
import scipy.stats as stats
import scipy.signal as signal
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import time
import sys
import warnings

warnings.filterwarnings('ignore')

nServices = 40


def waitforEnter():
    if sys.version_info[0] == 2:
        raw_input("Press ENTER to continue.")
    else:
        input("Press ENTER to continue.")


plt.ion()
data1 = np.loadtxt('../dataFiles/data1')

toShow = 1
plt.figure(0)

for i in range(0, nServices):
    if toShow == 6:
        plt.show()
        waitforEnter()
        plt.figure(i / 5)
        toShow = 1

    plt.subplot(5, 1, toShow)
    toShow = toShow + 1
    plt.plot(data1[:, i], marker='s', label='dataset ' + str(i))

plt.show()

# our profile

plt.figure(10)
waitforEnter()
data2_download = np.loadtxt('../dataFiles/Download')
data2_download *= 1048576 # convert to bytes

data2_download_tmp = []

# group by 2
for i in xrange(260, 600+260, 2):
    if i < len(data2_download) - 1:
        data2_download_tmp += [data2_download[i] + data2_download[i+1]]
    else:
        break

data2_download = data2_download_tmp

# for dataset 0 (from 0 to 39)
plt.plot(data2_download, marker='s', label='dataset ours')
plt.show()

# -2- #
M = np.mean(data1, axis=0)
Md = np.median(data1, axis=0)
V = np.var(data1, axis=0)
S = stats.skew(data1)
K = stats.kurtosis(data1)
p = range(5, 101, 1)
Pr = np.percentile(data1, p, axis=0)

M1 = np.mean(data2_download, axis=0)
Md1 = np.median(data2_download, axis=0)
V1 = np.var(data2_download, axis=0)
S1 = stats.skew(data2_download)
K1 = stats.kurtosis(data2_download)
p1 = range(5, 101, 1)
Pr1 = np.percentile(data2_download, p1, axis=0)

plt.figure(9)
plt.subplot(5, 1, 1)
plt.plot(M)
plt.plot([0, 39], [M1, M1], color="red")
plt.ylabel('mean')
plt.subplot(5, 1, 2)
plt.plot(Md)
plt.plot([0, 39], [Md1, Md1], color="red")
plt.ylabel('median')
plt.subplot(5, 1, 3)
plt.plot(V)
plt.plot([0, 39], [V1, V1], color="red")
plt.ylabel('variance')
plt.subplot(5, 1, 4)
plt.plot(S)
plt.plot([0, 39], [S1, S1], color="red")
plt.ylabel('skewness')
plt.subplot(5, 1, 5)
plt.plot(K)
plt.plot([0, 39], [K1, K1], color="red")
plt.ylabel('kurtosis')
plt.show()

# End
waitforEnter()
