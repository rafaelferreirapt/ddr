# coding=utf-8
import argparse
import itertools
import pickle

from collections import OrderedDict
from json_to_latex import JsonToLatex
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
        ws_delay[pair] = 0
        for i in range(0, len(path) - 1):
            ws_delay[pair] += net_tmp[path[i]][path[i + 1]]['delay']

    tmp_stats = listStats(ws_delay)

    # best solution
    if liststats_result is None or liststats_result[1] > tmp_stats[1]:
        allpairs_best = allpairs
        sol_best = sol.copy()
        ws_delay_best = ws_delay.copy()
        liststats_result = tmp_stats
        net_best = net_tmp.copy()

print('---')
print('Solution:' + str(sol_best))

# export to tex
table = []

for key, value in sol_best.items():
    table += [OrderedDict([
        ("Origem", key[0]),
        ("Destino", key[1]),
        ("Saltos", ", ".join(value)),
        ("Carga (pkts/sec)", net_best[key[0]][key[1]]['load'] if key[0] in net_best and key[1] in net_best[key[0]] else "Indisponível"),
        ("Atraso (micro/sec)", ("%0.2f" % ws_delay_best[(key[0], key[1])]))
    ])]

t = JsonToLatex(table, title="Solução obtida, carga nos links e atraso")
t.convert()
t.save("../report/tables/" + filename.replace(".dat", "_") + "netTE4.tex")
# export to tex

print('---')
for pair in allpairs_best:
    print("#flow %s-%s: %2.2f micro sec" % (pair[0], pair[1], ws_delay_best[(pair[0], pair[1])]))

meanWs, maxWs, maxWsK = listStats(ws_delay_best)
print('\n\nMean one-way delay: %.2f micro seg\nMaximum one-way delay: %.2f micro seg'
      '\nMaximum one-way delay flow %s-%s' % (meanWs, maxWs, maxWsK[0], maxWsK[1]))

# export to tex
table_stats1 = [OrderedDict({"Mean one-way delay": meanWs,
                             "Maximum one-way delay": maxWs,
                             "Maximum one-way delay flow": "%s-%s" % (maxWsK[0], maxWsK[1])})]

t = JsonToLatex(table_stats1, title="Atraso")
t.convert()
t.save("../report/tables/" + filename.replace(".dat", "_") + "netTE4_stats1.tex")
# export to tex

print('---')

loadAll = {}

for link in links:
    print("#link %s-%s: %d pkts/sec" % (link[0], link[1], net[link[0]][link[1]]['load']))
    print("#link %s-%s: %d pkts/sec" % (link[1], link[0], net[link[1]][link[0]]['load']))

    loadAll.update({(link[0], link[1]): net[link[0]][link[1]]['load']})
    loadAll.update({(link[1], link[0]): net[link[1]][link[0]]['load']})

meanLoad, maxLoad, maxLoadK = listStats(loadAll)
print('\n\nMean one-way load: %.2f pkts/sec\nMaximum one-way load: %.2f pkts/sec'
      '\nMax load flow %s-%s' % (meanLoad, maxLoad, maxLoadK[0], maxLoadK[1]))

# export to tex
table_stats2 = [OrderedDict({"Mean one-way load": "%.2f pkts/sec" % meanLoad,
                             "Maximum one-way load": "%.2f pkts/sec" % maxLoad,
                             "Max load flow": "%s-%s" % (maxLoadK[0], maxLoadK[1])})]

t = JsonToLatex(table_stats2, title="Carga")
t.convert()
t.save("../report/tables/" + filename.replace(".dat", "_") + "netTE4_stats2.tex")
# export to tex
