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

# our profile
data2_download = np.loadtxt('../dataFiles/Download')
data2_download *= 1048576  # convert to bytes

data2_download_tmp = []

# group by 2
for i in xrange(260, 600+260, 2):
    if i < len(data2_download) - 1:
        data2_download_tmp += [data2_download[i] + data2_download[i+1]]
    else:
        break

data2_download = data2_download_tmp

# ex 4
"""
# for dataset 0 (from 0 to 39)

for i in range(0, nServices):
    pdf, bins = np.histogram(data1[:, i], bins=50, density=True)
    dbin = np.diff(bins)[0]
    cdf = np.cumsum(pdf) * dbin
    x = bins[:-1]
    plt.figure(1)
    plt.plot(x, pdf, marker='s', c='blue', label='dataset 0 PDF')
    plt.show()

    plt.figure(2)
    plt.plot(x, cdf, marker='s', c='blue', label='dataset 0 CDF')
    plt.show()

    waitforEnter()

# for our profile pdf and cdf
pdf, bins = np.histogram(data2_download, bins=50, density=True)
dbin = np.diff(bins)[0]
cdf = np.cumsum(pdf) * dbin
x = bins[:-1]
plt.figure(1)
plt.plot(x, pdf, marker='s', c='blue', label='dataset 0 PDF')
plt.show()

plt.figure(2)
plt.plot(x, cdf, marker='s', c='blue', label='dataset 0 CDF')
plt.show()

waitforEnter()
# ex 5
# for dataset 0 (from 0 to 39)

for i in range(0, nServices-1):
    # i e i-1 ?? ou i com o our profile?

    plt.figure(3)
    plt.clf()
    p = range(5, 101, 1)
    Pr0 = np.percentile(data1[:, 0], p)
    Pr1 = np.percentile(data1[:, 1], p)
    plt.scatter(Pr0, Pr1, marker='o', c='blue')
    lp = [0, max(Pr0[-1], Pr1[-1])]
    plt.plot(lp, lp, c='red')
    plt.show()
    # P-P plot for dataset 0 and dataset 1
    plt.figure(4)
    plt.clf()
    pdf0, bins = np.histogram(data1[:, 0], bins=50, density=True)
    dbin = np.diff(bins)[0]
    cdf0 = np.cumsum(pdf0) * dbin
    # bins/xvalues of the CDF should be the same
    pdf1, bins = np.histogram(data1[:, 1], bins=bins, density=True)
    dbin = np.diff(bins)[0]
    cdf1 = np.cumsum(pdf1) * dbin
    plt.scatter(cdf0, cdf1, marker='o', c='blue')
    lp = [min(cdf0[0], cdf1[0]), 1]
    plt.plot(lp, lp, c='red')
    plt.show()

"""

# End
waitforEnter()
