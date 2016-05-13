import simpy
import numpy as np
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link
import json


if __name__ == '__main__':
    K = [64, 128]  # [64, 96, 128, 10000]
    B = 10e6
    tmp = 782  # 0.5*1500+0.5*64 bytes em media

    lambAI = [150, 600]
    lambBI = [150]
    lambIA = [450]
    lambIB = [150, 600]

    array = []

    muR = [500, 750, 1000]
    muL = 1.0*B/(tmp*8)

    for ai in lambAI:
        for bi in lambBI:
            for ia in lambIA:
                for ib in lambIB:
                    for k in K:
                        for r in muR:
                            loss_probability_nodes = 0
                            loss_probability_all = 0
                            loss_probability_links = 0
                            average_delay = 0
                            average_delayIA = 0
                            average_delayIB = 0
                            trans_band = 0
                            trans_bandIB = 0
                            trans_bandIA = 0
                            Wk = 0
                            WkIA = 0
                            WkIB = 0
                            for i in range(1, 4):
                                env = simpy.Environment()

                                txA = pkt_Sender(env, 'A', ai, 'I')
                                txB = pkt_Sender(env, 'B', bi, 'I')
                                txIA = pkt_Sender(env, 'I', ia, 'A')
                                txIB = pkt_Sender(env, 'I', ib, 'B')

                                rxI = pkt_Receiver(env, 'I')
                                rxA = pkt_Receiver(env, 'A')
                                rxB = pkt_Receiver(env, 'B')

                                node1 = Node(env, 'N1', r, k)
                                node2 = Node(env, 'N2', r, k)
                                node3 = Node(env, 'N3', r, k)
                                node4 = Node(env, 'N4', r, k)

                                link13 = Link(env, 'L1-3', B, k)
                                link23 = Link(env, 'L2-3', B, k)
                                link34 = Link(env, 'L3-4', B, k)
                                link4I = Link(env, 'L4-I', B, k)

                                link31 = Link(env, 'L3-1', B, k)
                                link32 = Link(env, 'L3-2', B, k)
                                link43 = Link(env, 'L4-3', B, k)
                                link1A = Link(env, 'L1-A', B, k)
                                link2B = Link(env, 'L2-B', B, k)

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

                                loss_probability_nodes += 100.0 * (all_packets_lost_node*1.0/all_packets_sent)
                                loss_probability_links += 100.0 * (all_packets_lost_links*1.0/all_packets_sent)
                                loss_probability_all += 100.0 * ((all_packets_lost_links+all_packets_lost_node)*1.0/all_packets_sent)

                                average_delay += 1.0 * rxI.overalldelay / rxI.packets_recv
                                average_delayIA += 1.0 * rxA.overalldelay / rxA.packets_recv
                                average_delayIB += 1.0 * rxB.overalldelay / rxB.packets_recv

                                trans_band += 1.0 * rxI.overallbytes / simtime
                                trans_bandIA += 1.0 * rxA.overallbytes / simtime
                                trans_bandIB += 1.0 * rxB.overallbytes / simtime

                                print("---- lambAI: %d, lambBI: %d, lambIA: %d, lambIB: %d"
                                      "queue size: %d, R: %d, B: %d, simtime: %d ----" % (ai, bi, ia, ib, k, r, B, simtime))
                                print('Loss probability nodes: %.2f%%' % loss_probability_nodes)
                                print('Loss probability links: %.2f%%' % loss_probability_links)
                                print('Loss probability: %.2f%%' % loss_probability_all)
                                print('Average delay: %f sec' % average_delay)
                                print('Average delay IA: %f sec' % average_delayIA)
                                print('Average delay IB: %f sec' % average_delayIB)
                                print('Transmitted bandwidth: %.1f Bytes/sec' % trans_band)
                                print('Transmitted bandwidth IA: %.1f Bytes/sec' % trans_bandIA)
                                print('Transmitted bandwidth IB: %.1f Bytes/sec' % trans_bandIB)

                                lambABI = bi+ai
                                lambIBA = ib+ia
                                tmpBI = r-bi-ib
                                tmpAI = r-ai-ia
                                tmpABI = r-lambABI-lambIBA

                                if tmpABI == 0:
                                    Wktmp = 1.0 * ai / (r-ai-ia) + 1.0 * ai / (muL-ai) + 1.0 * bi / (r-bi-ib) \
                                        + 1.0 * bi / (muL-bi) + 2.0 * lambABI / (muL-lambABI)

                                    WkIAtmp = 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ia / (muL-ia) + 1.0 * ia / (r-ia-ai)

                                    WkIBtmp = 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ib / (muL-ib) + 1.0 * ib / (r-ib - bi)
                                elif tmpAI == 0:
                                    Wktmp = 1.0 * ai / (muL-ai) + 1.0 * bi / (r-bi-ib) + 1.0 * bi / (muL-bi) + 2.0 * lambABI /\
                                        (r-lambABI-lambIBA) + 2.0 * lambABI / (muL-lambABI)

                                    WkIAtmp = 2.0 * lambIBA / (r-lambIBA-lambABI) + 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ia /\
                                        (muL-ia)

                                    WkIBtmp = 2.0 * lambIBA / (r-lambIBA - lambABI) + 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ib\
                                        / (muL-ib) + 1.0 * ib / (r-ib - bi)
                                elif tmpBI == 0:
                                    Wktmp = 1.0 * ai / (r-ai-ia) + 1.0 * ai / (muL-ai) + 1.0 * bi / (muL-bi) + 2.0 * lambABI /\
                                        (r-lambABI-lambIBA) + 2.0 * lambABI / (muL-lambABI)

                                    WkIAtmp = 2.0 * lambIBA / (r-lambIBA-lambABI) + 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ia /\
                                        (muL-ia) + 1.0 * ia / (r-ia-ai)

                                    WkIBtmp = 2.0 * lambIBA / (r-lambIBA - lambABI) + 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ib\
                                        / (muL-ib)

                                else:
                                    Wktmp = 1.0 * ai / (r-ai-ia) + 1.0 * ai / (muL-ai) + 1.0 * bi / (r-bi-ib) \
                                        + 1.0 * bi / (muL-bi) + 2.0 * lambABI / (r-lambABI-lambIBA) + 2.0 * lambABI /\
                                        (muL-lambABI)

                                    WkIAtmp = 2.0 * lambIBA / (r-lambIBA-lambABI) + 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ia /\
                                        (muL-ia) + 1.0 * ia / (r-ia-ai)

                                    WkIBtmp = 2.0 * lambIBA / (r-lambIBA - lambABI) + 1.0 * lambIBA / (muL-lambIBA) + 2.0 * ib\
                                        / (muL-ib) + 1.0 * ib / (r-ib - bi)

                                Wktmp /= lambABI
                                WkIAtmp /= lambIBA
                                WkIBtmp /= lambIBA

                                Wk += Wktmp
                                WkIA += WkIAtmp
                                WkIB += WkIBtmp

                            array.append({'lambdaAI': ai,
                                          'lambdaBI': bi,
                                          'lambdaIA': ia,
                                          'lamdbaIB': ib,
                                          'queueSize': k,
                                          'B': B,
                                          'R': r,
                                          'WkABI': round(Wk/3, 5),
                                          'WkIA': round(WkIA/3, 5),
                                          'WkIB': round(WkIB/3, 5),
                                          'Loss Probability nodes': round(loss_probability_nodes/3, 5),
                                          'Loss Probability links': round(loss_probability_links/3, 5),
                                          'Loss Probability': round(loss_probability_all/3, 5),
                                          'Average Delay ABI': round(average_delay/3, 5),
                                          'Average Delay IA': round(average_delayIA/3, 5),
                                          'Average Delay IB': round(average_delayIB/3, 5),
                                          'Transmitted bandwidth ABI': round(trans_band/3, 5),
                                          'Transmitted bandwidth IA': round(trans_bandIA/3, 5),
                                          'Transmitted bandwidth IB': round(trans_bandIB/3, 5)})

                            print ("Wk: %f" % (Wk/3))
                            print ("Wk IA: %f" % (WkIA/3))
                            print ("Wk IB: %f" % (WkIB/3))

    print array

    with open("pktSim7.json", "w") as outfile:
        json.dump(array, outfile)
