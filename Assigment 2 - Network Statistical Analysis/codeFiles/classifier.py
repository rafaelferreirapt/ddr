import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.covariance import EllipticEnvelope
import warnings
import sys

warnings.filterwarnings('ignore')

data1 = np.loadtxt('../dataFiles/data1')
data2 = np.loadtxt('../dataFiles/data2')

# our profile download
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

# our profile upload
data2_upload = np.loadtxt('../dataFiles/Upload')
data2_upload *= 1048576  # convert to bytes

data2_upload_tmp = []

# group by 2
for i in xrange(260, 600 + 260, 2):
    if i < len(data2_upload) - 1:
        data2_upload_tmp += [data2_upload[i] + data2_upload[i + 1]]
    else:
        break

data2_upload = data2_upload_tmp

# -WAIT- #


def wait_for_enter(message="Press ENTER to continue."):
    if sys.version_info[0] == 2:
        raw_input(message)
    else:
        input(message)


plt.ion()

# -14- #
# features
M1 = np.mean(data1, axis=0)
Md1 = np.median(data1, axis=0)
V1 = np.var(data1, axis=0)
S1 = stats.skew(data1)
K1 = stats.kurtosis(data1)
p = [25, 50, 75, 90, 95]
Pr1 = np.array(np.percentile(data1, p, axis=0)).T
M2 = np.mean(data2, axis=0)
Md2 = np.median(data2, axis=0)
V2 = np.var(data2, axis=0)
S2 = stats.skew(data2)
K2 = stats.kurtosis(data2)
Pr2 = np.array(np.percentile(data2, p, axis=0)).T
features = np.c_[M1, M2, Md1, Md2, V1, V2, S1, S2, K1, K2, Pr1, Pr2]

# features youtube
M1 = np.mean(data2_download, axis=0)
Md1 = np.median(data2_download, axis=0)
V1 = np.var(data2_download, axis=0)
S1 = stats.skew(data2_download)
K1 = stats.kurtosis(data2_download)
p = [25, 50, 75, 90, 95]
Pr1 = np.array(np.percentile(data2_download, p)).T
M2 = np.mean(data2_upload, axis=0)
Md2 = np.median(data2_upload, axis=0)
V2 = np.var(data2_upload, axis=0)
S2 = stats.skew(data2_upload)
K2 = stats.kurtosis(data2_upload)
Pr2 = np.array(np.percentile(data2_upload, p, axis=0)).T
features_youtube = np.r_[M1, M2, Md1, Md2, V1, V2, S1, S2, K1, K2, Pr1, Pr2]


# PCA

pca = PCA(n_components=2)
rcp = pca.fit(features).transform(features)
rcp_youtube = pca.transform(features_youtube)
plt.figure(13)
plt.scatter(rcp[0:19, 0], rcp[0:19, 1], marker='o', c='r', label='datasets 0-19')
plt.scatter(rcp[20:, 0], rcp[20:, 1], marker='s', c='b', label='datasets 20-39')
plt.scatter(rcp_youtube[0,0], rcp_youtube[0,1], marker='D', c='g', label='DataSet YouTube')
plt.legend()
plt.show()

#wait_for_enter()

# -15- #

rcp = PCA(n_components=2).fit_transform(features)
# K-means assuming 2 clusters
kmeans = KMeans(init='k-means++', n_clusters=2)
kmeans.fit(rcp)
kmeans.labels_
# vizualization plot
x_min, x_max = 1.5 * rcp[:, 0].min(), 1.5 * rcp[:, 0].max()
y_min, y_max = 1.5 * rcp[:, 1].min(), 1.5 * rcp[:, 1].max()


x_min_youtube, x_max_youtube = 1.5 * rcp_youtube[0, 0].min(), 1.5 * rcp_youtube[0, 0].max()
y_min_youtube, y_max_youtube = 1.5 * rcp_youtube[0, 1].min(), 1.5 * rcp_youtube[0, 1].max()

if x_min_youtube < x_min:
    x_min = x_min_youtube

if x_max_youtube > x_max:
    x_max = x_max_youtube

if y_min_youtube < y_min:
    y_min = y_min_youtube

if y_max_youtube > y_max:
    y_max = y_max_youtube

N = 20
hx = (x_max - x_min) / N
hy = (y_max - y_min) / N
xx, yy = np.meshgrid(np.arange(x_min, x_max, hx), np.arange(y_min, y_max, hy))
Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])
Z_youtube = kmeans.predict(np.r_[rcp_youtube[0,0], rcp_youtube[0,1]])

Z = Z.reshape(xx.shape)
plt.figure(14)
plt.imshow(Z, interpolation='nearest', extent=(xx.min(), xx.max(), yy.min(), yy.max()), cmap=plt.cm.Blues,
           aspect='auto', origin='lower', alpha=0.7)

plt.plot(rcp[:, 0], rcp[:, 1], 'ko')
plt.plot(rcp_youtube[0, 0], rcp_youtube[0, 1], marker='D', color='g', label='DataSet YouTube')
# Plot the centroids as a white X
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', color='r')
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.xticks(())
plt.yticks(())
plt.show()

#wait_for_enter()
# -16- #

# rcp = PCA(n_components=2).fit_transform(features)
# DBSCAN assuming a neighborhood maximum distance of 1e11
dbscan = DBSCAN(eps=1e11)
rcp_concat = np.r_[rcp, rcp_youtube]
dbscan.fit(rcp_concat)
L = dbscan.labels_
print(L)
colors = plt.cm.Blues(np.linspace(0, 1, len(set(L))))
plt.figure(15)
for l in set(L):
    p = (L == l)
    if l == -1:
        color = 'r'
    else:
        color = colors[l]
    plt.plot(rcp_concat[p, 0], rcp_concat[p, 1], 'o', c=color, markersize=10)
plt.show()

# -17- #

anom_perc = 4.5  # original 20
clf = EllipticEnvelope(contamination=.1)
clf.fit(rcp_concat)
clf.decision_function(rcp_concat).ravel()
pred = clf.decision_function(rcp_concat).ravel()
threshold = stats.scoreatpercentile(pred, anom_perc)
Anom = pred > threshold
print(Anom)
Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.figure(16)
plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), threshold, 7), cmap=plt.cm.Blues_r)
plt.contour(xx, yy, Z, levels=[threshold], linewidths=2, colors='red')
plt.plot(rcp_concat[:, 0], rcp_concat[:, 1], 'ko')
plt.show()

# End
wait_for_enter("END!")
