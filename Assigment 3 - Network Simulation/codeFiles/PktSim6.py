import simpy
import numpy as np
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link
import json

if __name__ == '__main__':
    K = [64, 256]  # [64, 96, 128, 10000]
    B = 10e6
    tmp = 782  # 0.5*1500+0.5*64 bytes em media

    lambAI = [150, 600]
    lambBI = [150, 600]

    array = []

    muR = [500, 750, 1000]
    muL = 1.0 * B / (tmp * 8)

    for a in lambAI:
        for b in lambBI:
            for k in K:
                for r in muR:
                    env = simpy.Environment()

                    txA = pkt_Sender(env, 'A', a, 'I')
                    txB = pkt_Sender(env, 'B', b, 'I')

                    rxI = pkt_Receiver(env, 'I')

                    node1 = Node(env, 'N1', r, k)
                    node2 = Node(env, 'N2', r, k)
                    node3 = Node(env, 'N3', r, k)
                    node4 = Node(env, 'N4', r, k)

                    link13 = Link(env, 'L1-3', B, k)
                    link23 = Link(env, 'L2-3', B, k)
                    link34 = Link(env, 'L3-4', B, k)
                    link4I = Link(env, 'L4-I', B, k)

                    txA.out = node1
                    txB.out = node2

                    node1.add_conn(link13, 'I')
                    node2.add_conn(link23, 'I')
                    node3.add_conn(link34, 'I')
                    node4.add_conn(link4I, 'I')

                    link13.out = node3
                    link23.out = node3
                    link34.out = node4
                    link4I.out = rxI

                    simtime = 200

                    env.run(simtime)

                    all_packets_sent = txA.packets_sent + txB.packets_sent
                    all_packets_lost_node = node1.lost_pkts + node2.lost_pkts + node3.lost_pkts + node4.lost_pkts
                    all_packets_lost_links = link13.lost_pkts + link23.lost_pkts + link34.lost_pkts + link4I.lost_pkts

                    loss_probability_nodes = 100.0 * (all_packets_lost_node * 1.0 / all_packets_sent)
                    loss_probability_links = 100.0 * (all_packets_lost_links * 1.0 / all_packets_sent)
                    loss_probability_all = 100.0 * (
                        (all_packets_lost_links + all_packets_lost_node) * 1.0 / all_packets_sent)

                    average_delay = 1.0 * rxI.overalldelay / rxI.packets_recv
                    trans_band = 1.0 * rxI.overallbytes / simtime

                    print("---- lambAI: %d, lambBI: %d, queue size: %d, B: %d, R: %d, simtime: %d ----" % (
                        a, b, k, B, r, simtime))
                    print('Loss probability nodes: %.2f%%' % loss_probability_nodes)
                    print('Loss probability links: %.2f%%' % loss_probability_links)
                    print('Loss probability: %.2f%%' % loss_probability_all)
                    print('Average delay: %f sec' % average_delay)
                    print('Transmitted bandwidth: %.1f Bytes/sec' % trans_band)

                    lambABI = b + a
                    tmpl = r - lambABI

                    if tmpl != 0:
                        Wk = ((1.0 * a) / (r - a)) + ((1.0 * a) / (muL - a)) + ((1.0 * b) / (r - b)) \
                             + ((1.0 * b) / (muL - b)) + ((2.0 * lambABI) / (r - lambABI)) + \
                             ((2.0 * lambABI) / (muL - lambABI))
                    else:
                        Wk = ((1.0 * a) / (r - a)) + ((1.0 * a) / (muL - a)) + ((1.0 * b) / (r - b)) + \
                             ((1.0 * b) / (muL - b)) + ((2.0 * lambABI) / (muL - lambABI))
                    Wk /= lambABI

                    array.append({'lambdaAI': a,
                                  'lambdaBI': b,
                                  'queueSize': k,
                                  'B': B,
                                  'R': r,
                                  'Wk': round(Wk, 5),
                                  'Loss Probability nodes': round(loss_probability_nodes, 5),
                                  'Loss Probability links': round(loss_probability_links, 5),
                                  'Loss Probability': round(loss_probability_all, 5),
                                  'Average Delay': round(average_delay, 5),
                                  'Transmitted bandwidth': round(trans_band, 5)})

                    print ("Wk: %f" % Wk)

    print array

    with open("pktSim6.json", "w") as outfile:
        json.dump(array, outfile)
