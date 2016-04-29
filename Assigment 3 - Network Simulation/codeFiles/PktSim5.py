import simpy
import numpy as np
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link
import json


if __name__ == '__main__':
    # Sender (tx) -> Node1 -> Link -> Receiver (rx)

    lamb = [150, 300, 450]
    K = [64, 96, 128, 10000]
    B = 2e6
    tmp = 782  # 0.5*1500+0.5*64 bytes em media
    mu = 1.0*B/(tmp*8)

    array = []

    for lam in lamb:
        for k in K:
            env = simpy.Environment()

            rx = pkt_Receiver(env, 'B')
            tx = pkt_Sender(env, 'A', lam, 'B')
            node1 = Node(env, 'N1', 300, k)
            link1 = Link(env, 'L1', B, k)

            tx.out = node1
            node1.add_conn(link1, 'B')
            link1.out = rx

            simtime = 50
            env.run(simtime)

            loss_probability = 100.0 * (tx.packets_sent-rx.packets_recv)/tx.packets_sent
            average_delay = 1.0 * rx.overalldelay / rx.packets_recv
            trans_band = 1.0 * rx.overallbytes / simtime

            print("---- lambda: %d, queue size: %d, B: %d, simtime: %d ----" % (lam, k, B, simtime))
            print('Loss probability: %.2f%%' % loss_probability)
            print('Average delay: %f sec' % average_delay)
            print('Transmitted bandwidth: %.1f Bytes/sec' % trans_band)

            Wk = 2.0 / (mu-lam)
            array.append({'lambda': lam,
                          'queueSize': k,
                          'Wk': Wk,
                          'Loss Probability': loss_probability,
                          'Average Delay': average_delay,
                          'Transmitted bandwidth': trans_band})

            print ("Wk: %f" % Wk)

    print array

    with open("pktSim5.json", "w") as outfile:
        json.dump(array, outfile)
