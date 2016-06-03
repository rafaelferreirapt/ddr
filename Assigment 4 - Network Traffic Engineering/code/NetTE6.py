# coding=utf-8
import argparse
import itertools
import pickle

import random
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from collections import OrderedDict
from json_to_latex import JsonToLatex
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

sol_local = {}
ws_delay_local = {}
liststats_local = None
net_local = nx.DiGraph()

for k in range(0, 10000):
    net_tmp = net.copy()
    allpairs = list(itertools.permutations(nodes, 2))

    sol = {}

    ws_delay = {}

    random.shuffle(allpairs)

    for pair in allpairs:
        path = nx.shortest_path(net_tmp, pair[0], pair[1], weight='delay')
        sol.update({pair: path})

        for i in range(0, len(path) - 1):
            net_tmp[path[i]][path[i + 1]]['load'] += tm[pair[0]][pair[1]]
            net_tmp[path[i]][path[i + 1]]['delay'] = 1e6 / (mu - net_tmp[path[i]][path[i + 1]]['load'])
            # imprescendivel por causa do weight delay

    """
    Local Search
    """
    for pair in allpairs:
        sol_tmp = sol.copy()
        net_tmp_local = net_tmp.copy()

        ws_delay = {}

        path = sol_tmp[pair]
        del sol_tmp[pair]

        for i in range(0, len(path) - 1):
            net_tmp_local[path[i]][path[i + 1]]['load'] -= tm[pair[0]][pair[1]]
            net_tmp_local[path[i]][path[i + 1]]['delay'] = 1e6 / (mu - net_tmp_local[path[i]][path[i + 1]]['load'])

        path = nx.shortest_path(net_tmp_local, pair[0], pair[1], weight='delay')
        sol_tmp.update({pair: path})

        for i in range(0, len(path) - 1):
            net_tmp_local[path[i]][path[i + 1]]['load'] += tm[pair[0]][pair[1]]
            net_tmp_local[path[i]][path[i + 1]]['delay'] = 1e6 / (mu - net_tmp_local[path[i]][path[i + 1]]['load'])

        for p in allpairs:
            path = sol_tmp[p]
            ws_delay[p] = 0
            for i in range(0, len(path) - 1):
                ws_delay[p] += net_tmp_local[path[i]][path[i + 1]]['delay']

        tmp_stats = listStats(ws_delay)

        # best solution
        if liststats_local is None or liststats_local[1] > tmp_stats[1]:
            sol_local = sol_tmp.copy()
            ws_delay_local = ws_delay.copy()
            liststats_local = tmp_stats
            net_local = net_tmp_local.copy()


print('---')
print('Solution:' + str(sol_local))

# export to tex
table = []

for key, value in sol_local.items():
    table += [OrderedDict([
        ("Origem", key[0]),
        ("Destino", key[1]),
        ("Saltos", ", ".join(value)),
        ("Carga (pkts/sec)", net_local[key[0]][key[1]]['load'] if key[0] in net_local and key[1] in net_local[key[0]] else "Indisponível"),
        ("Atraso (micro/sec)", ("%0.2f" % ws_delay_local[(key[0], key[1])]))
    ])]

t = JsonToLatex(table, title="Solução obtida, carga nos links e atraso")
t.convert()
t.save("../report/tables/" + filename.replace(".dat", "_") + "netTE6.tex")
# export to tex

print('---')
for pair in allpairs:
    print("#flow %s-%s: %2.2f micro sec" % (pair[0], pair[1], ws_delay_local[(pair[0], pair[1])]))

meanWs, maxWs, maxWsK = listStats(ws_delay_local)
print('\n\nMean one-way delay: %.2f micro seg\nMaximum one-way delay: %.2f micro seg'
      '\nMaximum one-way delay flow %s-%s' % (meanWs, maxWs, maxWsK[0], maxWsK[1]))

# export to tex
table_stats1 = [OrderedDict({"Mean one-way delay": meanWs,
                             "Maximum one-way delay": maxWs,
                             "Maximum one-way delay flow": "%s-%s" % (maxWsK[0], maxWsK[1])})]

t = JsonToLatex(table_stats1, title="Atraso")
t.convert()
t.save("../report/tables/" + filename.replace(".dat", "_") + "netTE6_stats1.tex")
# export to tex

print('---')

loadAll = {}

for link in links:
    print("#link %s-%s: %d pkts/sec" % (link[0], link[1], net_local[link[0]][link[1]]['load']))
    print("#link %s-%s: %d pkts/sec" % (link[1], link[0], net_local[link[1]][link[0]]['load']))

    loadAll.update({(link[0], link[1]): net_local[link[0]][link[1]]['load']})
    loadAll.update({(link[1], link[0]): net_local[link[1]][link[0]]['load']})

meanLoad, maxLoad, maxLoadK = listStats(loadAll)
print('\n\nMean one-way load: %.2f pkts/sec\nMaximum one-way load: %.2f pkts/sec'
      '\nMax load flow %s-%s' % (meanLoad, maxLoad, maxLoadK[0], maxLoadK[1]))

# export to tex
table_stats2 = [OrderedDict({"Mean one-way load": "%.2f pkts/sec" % meanLoad,
                             "Maximum one-way load": "%.2f pkts/sec" % maxLoad,
                             "Max load flow": "%s-%s" % (maxLoadK[0], maxLoadK[1])})]

t = JsonToLatex(table_stats2, title="Carga")
t.convert()
t.save("../report/tables/" + filename.replace(".dat", "_") + "netTE6_stats2.tex")
# export to tex
