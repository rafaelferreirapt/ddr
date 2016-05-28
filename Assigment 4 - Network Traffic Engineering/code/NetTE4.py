import argparse
import itertools
import pickle

import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from mygeo import geodist

mu = 1e9 / 8000  # link speed in pkts/sec
lightspeed = 300000.0  # Km/sec


def listStats(L):
    # Returns the mean and maximum values of a list of numbers with generic keys
    # returns also the key of the maximum value
    V = L.values()
    K = L.keys()
    meanL = np.mean(V)
    maxL = np.max(V)
    p = np.where(V == maxL)[0][0]
    maxLK = K[p]
    return meanL, maxL, maxLK


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', nargs='?', help='input network file', default='network.dat')
args = parser.parse_args()

filename = args.file

with open(filename) as f:
    nodes, links, pos, tm = pickle.load(f)

print(tm)

net = nx.DiGraph()
for node in nodes:
    net.add_node(node)

for link in links:
    dist = geodist((pos[link[0]][1], pos[link[0]][0]), (pos[link[1]][1], pos[link[1]][0]))
    net.add_edge(link[0], link[1], distance=dist, load=0, delay=0)
    net.add_edge(link[1], link[0], distance=dist, load=0, delay=0)
# print(link,dist,(pos[link[0]][1],pos[link[0]][0]),(pos[link[1]][1],pos[link[1]][0]))

nx.draw(net, pos, with_labels=True)
# plt.show()

allpairs_best = []
sol_best = {}
ws_delay_best = {}
liststats_result = None
net_best = nx.DiGraph()

for i in range(0, 10000):
    allpairs = list(itertools.permutations(nodes, 2))
    sol = {}

    ws_delay = {}

    random.shuffle(allpairs)

    net_tmp = net.copy()

    for pair in allpairs:
        path = nx.shortest_path(net_tmp, pair[0], pair[1], weight='delay')
        sol.update({pair: path})

        for i in range(0, len(path) - 1):
            net_tmp[path[i]][path[i + 1]]['load'] += tm[pair[0]][pair[1]]
            net_tmp[path[i]][path[i + 1]]['delay'] = 1e6 / (mu - net_tmp[path[i]][path[i + 1]]['load'])

    for pair in allpairs:
        path = sol[pair]
        for i in range(0, len(path) - 1):
            ws_delay[pair] = net[path[i]][path[i + 1]]['delay']

    tmp_stats = listStats(ws_delay)

    # best solution
    if liststats_result is None or liststats_result[1] > tmp_stats[1]:
        allpairs_best = allpairs
        sol_best = sol
        ws_delay_best = ws_delay
        liststats_result = tmp_stats
        net_best = net_tmp

print('---')
print('Solution:' + str(sol_best))

print('---')
for pair in allpairs_best:
    print("#flow %s-%s: %2.2f micro sec" % (pair[0], pair[1], ws_delay_best[(pair[0], pair[1])]))

meanWs, maxWs, maxWsK = listStats(ws_delay_best)
print('\n\nMean one-way delay: %.2f micro seg\nMaximum one-way delay: %.2f micro seg'
      '\nflow %s-%s' % (meanWs, maxWs, maxWsK[0], maxWsK[1]))

print('---')

delayAll = {}

for link in links:
    print("#link %s-%s: %f micro seg" % (link[0], link[1], net_best[link[0]][link[1]]['delay']))
    print("#link %s-%s: %f micro seg" % (link[1], link[0], net_best[link[1]][link[0]]['delay']))

    delayAll.update({(link[0], link[1]): net_best[link[0]][link[1]]['delay']})
    delayAll.update({(link[1], link[0]): net_best[link[1]][link[0]]['delay']})

meanLoad, maxLoad, maxLoadK = listStats(delayAll)
print('\n\nMean one-way delay: %f micro seg\nMaximum one-way delay: %f micro seg'
      '\nflow %s-%s' % (meanLoad, maxLoad, maxLoadK[0], maxLoadK[1]))
