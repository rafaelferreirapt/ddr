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
            Wk = 0
            loss_probability = 0
            average_delay = 0
            trans_band = 0
            for i in range(1, 4):
                env = simpy.Environment()

                rx = pkt_Receiver(env, 'B')
                tx = pkt_Sender(env, 'A', lam, 'B')
                node1 = Node(env, 'N1', 300, k)
                link1 = Link(env, 'L1', B, k)

                tx.out = node1
                node1.add_conn(link1, 'B')
                link1.out = rx

                if k == 10000:
                    simtime = 500
                else:
                    simtime = 30

                env.run(simtime)

                loss_probability += 100.0 * (tx.packets_sent-rx.packets_recv)/tx.packets_sent
                average_delay += 1.0 * rx.overalldelay / rx.packets_recv
                trans_band += 1.0 * rx.overallbytes / simtime

                print("---- lambda: %d, queue size: %d, B: %d, simtime: %d ----" % (lam, k, B, simtime))
                print('Loss probability: %.2f%%' % loss_probability)
                print('Average delay: %f sec' % average_delay)
                print('Transmitted bandwidth: %.1f Bytes/sec' % trans_band)

                Wk += 2.0 / (mu-lam)
            array.append({'lambda': lam,
                          'queueSize': k,
                          'Wk': round(Wk/3, 5),
                          'Loss Probability': round(loss_probability/3, 5),
                          'Average Delay': round(average_delay/3, 5),
                          'Transmitted bandwidth': round(trans_band/3, 5)})

            print ("Wk: %f" % (Wk/3))

    print array

    with open("pktSim5.json", "w") as outfile:
        json.dump(array, outfile)
