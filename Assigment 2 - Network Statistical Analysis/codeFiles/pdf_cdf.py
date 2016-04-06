import numpy as np
from scipy import stats
import matplotlib.mlab as mlab
from scipy.signal import periodogram
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
for i in xrange(260, 600 + 260, 2):
    if i < len(data2_download) - 1:
        data2_download_tmp += [data2_download[i] + data2_download[i + 1]]
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
    plt.savefig("../imagens/qq_plot_e_pp_plot/qq_plot_"+str(i)+".png")

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
    plt.savefig("../imagens/qq_plot_e_pp_plot/pp_plot_"+str(i)+".png")
    waitforEnter()

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
for i in range(0, nServices + 1):
    if i == nServices:
        np_data_1 = data2_download
    else:
        np_data_1 = data1[:, i]

    for x in range(0, nServices + 1):
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
plt.savefig("../imagens/hellinger_distance/Relative_distances_between_PDFs_using_Hellinger_distance.png")

fig = plt.figure(6)
fig.suptitle('Relative distances between PDFs using Hellinger distance', fontsize=14)

B = np.zeros((1, 40))

for i in range(0, nServices):
    pdf0, bins = np.histogram(data1[:, i], bins=50, density=True)
    pdf1, bins = np.histogram(data2_download, bins=bins, density=True)

    B[0, i] = hellingerDist(pdf0, pdf1)

plt.plot(B[0, :], marker='s', c='blue')
plt.savefig("../imagens/hellinger_distance/Relative_distances_between_PDFs_using_Hellinger_distance_plot.png")

fig = plt.figure(7)
fig.suptitle("Kolmogorov-Smirnov test", fontsize=14)
plt.pcolormesh(A)
plt.show()
plt.savefig("../imagens/hellinger_distance/Kolmogorov-Smirnov_test.png")

# ex 8
data2 = np.loadtxt('../dataFiles/data2')
plt.figure(45)

for i in range(0, 40):
    pdf, x, y = np.histogram2d(data1[:, i], data2[:, i], bins=10)
    xx, yy = np.meshgrid(x, y)
    plt.pcolormesh(xx, yy, pdf)
    plt.show()
    plt.savefig("../imagens/Multivariate_Distributions/histogram2d_serv_"+str(i)+".png")

waitforEnter()

# -9- #
plt.figure(46)
data1All = np.loadtxt('../dataFiles/data1All')

for a in range(20, 501, 20):
    plt.clf()
    Agg = np.sum(data1All[:, 0:a], axis=1)
    pdf, x = np.histogram(Agg, bins=20, density=True)
    m = np.mean(Agg)
    std = np.std(Agg)  # standard deviation = sqrt( variance )
    plt.plot(x[:-1], pdf, 'k', label='empirical PDF (' + str(a) + ' users)')
    plt.plot(x, mlab.normpdf(x, m, std), 'r', label='inferred Gaussian PDF')
    plt.show()
    plt.savefig("../imagens/aggregation_effect/empirical PDF (" + str(a) + " users).png")
    plt.legend()
    waitforEnter()


# -10- #
plt.figure(47)
traff = np.loadtxt('../dataFiles/traff')
C = abs(np.corrcoef(traff, rowvar=0))
plt.pcolormesh(C)
plt.show()
plt.savefig("../imagens/event_correlation/event_correlation.png")


waitforEnter()


# -11- #
# for dataset 2
plt.figure(48)

for a in range(0, 40, 1):
    plt.clf()

    x = data1[:, a]
    lag = np.arange(0, 100, 1)
    xcorr = np.zeros(100)
    xcorr[0] = np.correlate(x, x)
    for l in lag[1:]:
        xcorr[l] = np.correlate(x[:-l], x[l:])
    plt.plot(lag, xcorr)
    plt.show()
    plt.savefig("../imagens/periodicity/periodicity_service_" + str(a) + ".png")

waitforEnter()

# install:
#sudo apt-get install python-numpy python-scipy python-matplotlib ipython ipython-notebook python-pandas python-sympy python-nose
# sudo pip install scipy --upgrade
# -12- #
# for dataset 2 (with modulus-squared of FFT)
plt.figure(49)

for a in range(0, 40, 1):
    plt.clf()
    x = data1[:, a]
    fft = np.fft.fft(x)
    psd = abs(fft) ** 2
    plt.plot(psd[:50])
    plt.show()
    # for dataset 2 (with Welch's method )
    f, psd = periodogram(x)
    plt.plot(1 / f[:50], psd[:50])
    plt.show()
    plt.savefig("../imagens/periodogram/periodogram" + str(a) + ".png")

waitforEnter()
"""

# -13- #
import scalogram


for a in range(0, 40, 1):
    plt.clf()
    plt.figure(50)

    x = data1[:, a]
    scales = np.arange(1, 50)
    plt.ion()
    cwt = scalogram.CWTfft(x, scales)
    plt.imshow(abs(cwt), cmap=plt.cm.Blues, aspect='auto')
    plt.show()
    plt.savefig("../imagens/scalogram/scalogramfft" + str(a) + ".png")
    plt.clf()

    plt.figure(51)

    S, scales = scalogram.scalogramCWT(x, scales)
    plt.plot(scales, S)
    plt.show()
    plt.savefig("../imagens/scalogram/scalogramCWT" + str(a) + ".png")


waitforEnter()


# End
waitforEnter()

