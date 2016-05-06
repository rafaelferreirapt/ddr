import simpy
import numpy as np
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link
import json


if __name__ == '__main__':
    K = 64  # [64, 96, 128, 10000]
    B = 10e6
    tmp = 782  # 0.5*1500+0.5*64 bytes em media

    lambAI = 150
    lambBI = 150
    lambIA = 150
    lambIB = 150

    array = []

    muR = 500
    muL = 1.0*B/(tmp*8)

    env = simpy.Environment()

    txA = pkt_Sender(env, 'A', lambAI, 'I')
    txB = pkt_Sender(env, 'B', lambBI, 'I')
    txIA = pkt_Sender(env, 'I', lambIA, 'A')
    txIB = pkt_Sender(env, 'I', lambIB, 'B')

    rxI = pkt_Receiver(env, 'I')
    rxA = pkt_Receiver(env, 'A')
    rxB = pkt_Receiver(env, 'B')

    node1 = Node(env, 'N1', muR, K)
    node2 = Node(env, 'N2', muR, K)
    node3 = Node(env, 'N3', muR, K)
    node4 = Node(env, 'N4', muR, K)

    link13 = Link(env, 'L1-3', B, K)
    link23 = Link(env, 'L2-3', B, K)
    link34 = Link(env, 'L3-4', B, K)
    link4I = Link(env, 'L4-I', B, K)

    link31 = Link(env, 'L3-1', B, K)
    link32 = Link(env, 'L3-2', B, K)
    link43 = Link(env, 'L4-3', B, K)
    link1A = Link(env, 'L1-A', B, K)
    link2B = Link(env, 'L2-B', B, K)

    txA.out = node1
    txB.out = node2
    txIA.out = node4
    txIB.out = node4

    node1.add_conn(link13, 'I')
    node1.add_conn(link1A, 'A')

    node2.add_conn(link23, 'I')
    node2.add_conn(link2B, 'B')

    node3.add_conn(link34, 'I')
    node3.add_conn(link31, 'A')
    node3.add_conn(link32, 'B')

    node4.add_conn(link4I, 'I')
    node4.add_conn(link43, ['A', 'B'])

    link13.out = node3
    link23.out = node3
    link34.out = node4
    link4I.out = rxI

    link31.out = node1
    link32.out = node2
    link43.out = node3
    link1A.out = rxA
    link2B.out = rxB

    simtime = 200

    env.run(simtime)

    all_packets_sent = txA.packets_sent + txB.packets_sent + txIA.packets_sent + txIB.packets_sent
    all_packets_lost_node = node1.lost_pkts + node2.lost_pkts + node3.lost_pkts + node4.lost_pkts
    all_packets_lost_links = link13.lost_pkts + link23.lost_pkts + link34.lost_pkts + link4I.lost_pkts \
        + link31.lost_pkts + link32.lost_pkts + link43.lost_pkts + link1A.lost_pkts + link2B.lost_pkts

    loss_probability_nodes = 100.0 * (all_packets_lost_node*1.0/all_packets_sent)
    loss_probability_links = 100.0 * (all_packets_lost_links*1.0/all_packets_sent)
    loss_probability_all = 100.0 * ((all_packets_lost_links+all_packets_lost_node)*1.0/all_packets_sent)

    average_delay = 1.0 * rxI.overalldelay / rxI.packets_recv
    average_delayIA = 1.0 * rxA.overalldelay / rxA.packets_recv
    average_delayIB = 1.0 * rxB.overalldelay / rxB.packets_recv

    trans_band = 1.0 * rxI.overallbytes / simtime
    trans_bandIA = 1.0 * rxA.overallbytes / simtime
    trans_bandIB = 1.0 * rxB.overallbytes / simtime

    print("---- lambAI: %d, lambBI: %d, lambIA: %d, lambIB: %d"
          "queue size: %d, B: %d, simtime: %d ----" % (lambAI, lambBI, lambIA, lambIB, K, B, simtime))
    print('Loss probability nodes: %.2f%%' % loss_probability_nodes)
    print('Loss probability links: %.2f%%' % loss_probability_links)
    print('Loss probability: %.2f%%' % loss_probability_all)
    print('Average delay: %f sec' % average_delay)
    print('Average delay: %f sec' % average_delay)
    print('Average delay: %f sec' % average_delay)
    print('Transmitted bandwidth: %.1f Bytes/sec' % trans_band)

    lambABI = lambBI+lambAI

    Wk = 1.0 * lambAI / (muR-lambAI) + 1.0 * lambAI / (muL-lambAI) + 1.0 * lambBI / (muR-lambBI) \
        + 1.0 * lambBI / (muL-lambBI) + 2.0 * lambABI / (muR-lambABI) + 2.0 * lambABI / (muL-lambABI)
    Wk /= lambABI

    array.append({'lambdaAI': lambAI,
                  'lambdaBI': lambBI,
                  'queueSize': K,
                  'B': B,
                  'Wk': Wk,
                  'Loss Probability nodes': loss_probability_nodes,
                  'Loss Probability links': loss_probability_links,
                  'Loss Probability': loss_probability_all,
                  'Average Delay': average_delay,
                  'Transmitted bandwidth': trans_band})

    print ("Wk: %f" % Wk)

    print array

    with open("pktSim7.json", "w") as outfile:
        json.dump(array, outfile)
