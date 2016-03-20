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
"""
# ex 4
# for dataset 0 (from 0 to 39)

# PDF

fig = plt.figure(1)
fig.suptitle('Probability Density Functions (PDF)', fontsize=14)

for i in range(0, nServices):
    pdf, bins = np.histogram(data1[:, i], bins=50, density=True)
    x = bins[:-1]
    if i < 20:
        plt.plot(x, pdf, marker='s', c='blue', label='datasets 0 - 19')
    else:
        plt.plot(x, pdf, marker='s', c='red', label='datasets 20 - 39')
    plt.show()

# for our profile pdf and cdf
pdf, bins = np.histogram(data2_download, bins=50, density=True)
x = bins[:-1]
plt.plot(x, pdf, marker='s', c='green', label='dataset our PDF')
plt.yscale('log')
plt.show()

# CDF

fig = plt.figure(2)
fig.suptitle('Cumulative Distribution Function (CDF)', fontsize=14)

for i in range(0, nServices):
    pdf, bins = np.histogram(data1[:, i], bins=50, density=True)
    dbin = np.diff(bins)[0]
    cdf = np.cumsum(pdf) * dbin
    x = bins[:-1]
    if i < 20:
        plt.plot(x, cdf, marker='s', c='blue', label='datasets 0 - 19')
    else:
        plt.plot(x, cdf, marker='s', c='red', label='datasets 20 - 39')
    plt.show()

# for our profile pdf and cdf
pdf, bins = np.histogram(data2_download, bins=50, density=True)
dbin = np.diff(bins)[0]
cdf = np.cumsum(pdf) * dbin
x = bins[:-1]

plt.plot(x, cdf, marker='s', c='green', label='dataset our CDF')
plt.show()


waitforEnter()

# ex 5

# for dataset 0 (from 0 to 39)
for i in range(0, nServices):
    fig = plt.figure(3)
    plt.clf()
    fig.suptitle('Q-Q plot for dataset ' + str(i) + ' with our profile', fontsize=14)
    p = range(5, 101, 1)
    Pr0 = np.percentile(data1[:, i], p)
    Pr1 = np.percentile(data2_download, p)
    plt.scatter(Pr0, Pr1, marker='o', c='blue')
    lp = [0, max(Pr0[-1], Pr1[-1])]
    plt.plot(lp, lp, c='red')
    plt.show()

    # P-P plot for dataset 0 and dataset 1

    fig = plt.figure(4)
    plt.clf()
    fig.suptitle('P-P plot for dataset ' + str(i) + ' with our profile', fontsize=14)
    pdf0, bins = np.histogram(data1[:, i], bins=50, density=True)
    dbin = np.diff(bins)[0]
    cdf0 = np.cumsum(pdf0) * dbin
    # bins/xvalues of the CDF should be the same
    pdf1, bins = np.histogram(data2_download, bins=bins, density=True)
    dbin = np.diff(bins)[0]
    cdf1 = np.cumsum(pdf1) * dbin
    plt.scatter(cdf0, cdf1, marker='o', c='blue')
    lp = [min(cdf0[0], cdf1[0]), 1]
    plt.plot(lp, lp, c='red')
    plt.show()
    waitforEnter()

"""
# ex 6
def hellingerDist(pdf1, pdf2):
    return np.sqrt(np.sum((np.sqrt(pdf1) - np.sqrt(pdf2)) ** 2)) / np.sqrt(2)


C = np.zeros((41, 41))

# ex 7
# for dataset 0
# nao conseguimos ajustar
# stats.kstest(data1[:, 0], 'expon')
# stats.kstest(data1[:, 0], 'norm')
A = np.zeros((41, 41))

# for dataset 0 (from 0 to 39)
for i in range(0, nServices+1):
    if i == nServices:
        np_data_1 = data2_download
    else:
        np_data_1 = data1[:, i]

    for x in range(0, nServices+1):
        if x == nServices:
            np_data_2 = data2_download
        else:
            np_data_2 = data1[:, x]

        pdf0, bins = np.histogram(np_data_1, bins=50, density=True)
        pdf1, bins = np.histogram(np_data_2, bins=bins, density=True)

        C[i, x] = hellingerDist(pdf0, pdf1)

        D, p_value = stats.ks_2samp(np_data_1, np_data_2)

        if p_value < 0.05:
            A[i, x] = 0
        else:
            A[i, x] = 1

fig = plt.figure(5)
fig.suptitle('Relative distances between PDFs using Hellinger distance', fontsize=14)
plt.pcolormesh(C)
plt.show()

fig = plt.figure(6)
fig.suptitle('Relative distances between PDFs using Hellinger distance', fontsize=14)

B = np.zeros((1, 40))

for i in range(0, nServices):
    pdf0, bins = np.histogram(data1[:, i], bins=50, density=True)
    pdf1, bins = np.histogram(data2_download, bins=bins, density=True)

    B[0, i] = hellingerDist(pdf0, pdf1)

plt.plot(B[0, :], marker='s', c='blue')

fig = plt.figure(7)
fig.suptitle('ALGO', fontsize=14)
plt.pcolormesh(A)
plt.show()

# End
waitforEnter()
