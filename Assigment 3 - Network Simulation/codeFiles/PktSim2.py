import simpy
import numpy as np
# sudo apt-get install libmpfr-dev
# sudo pip install bigfloat
import bigfloat
import json
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link, Packet


if __name__ == '__main__':
    # Sender (tx) -> Node1 -> Link -> Receiver (rx)

    lamb = [150, 300, 450]
    K = [64, 96, 128, 10000]
    B = 10e9
    tmp = 782  # 0.5*1500+0.5*64 bytes em media

    array = []

    for lam in lamb:
        for k in K:
            Wmm1 = 0
            Wmd1 = 0
            Wmg1 = 0
            Wmmk = 0
            pb = 0
            loss_probability = 0
            average_delay = 0
            trans_band = 0
            for i in range(1, 4):
                env = simpy.Environment()

                rx = pkt_Receiver(env, 'B')
                tx = pkt_Sender(env, 'A', lam, 'B')
                node2 = Node(env, 'N1', 350, k)
                link = Link(env, 'L', B, np.inf)

                tx.out = node2
                node2.add_conn(link, 'B')
                link.out = rx

                if k == 10000:
                    simtime = 500
                else:
                    simtime = 30
                env.run(simtime)

                loss_probability += 100.0 * (tx.packets_sent-rx.packets_recv)/tx.packets_sent
                average_delay += 1.0 * rx.overalldelay / rx.packets_recv
                trans_band += 1.0 * rx.overallbytes / simtime

                print("---- lambda: %d, queue size: %d, B: %d, simtime: %d ----" % (lam, k, B, simtime))
                print('(1) Loss probability: %.2f%%' % (100.0*((tx.packets_sent-rx.packets_recv)/tx.packets_sent)))
                print('(2) Loss probability: %.2f%%' % (100.0 * node2.lost_pkts / tx.packets_sent))
                print('Average delay: %f sec' % (1.0 * rx.overalldelay / rx.packets_recv))
                print('Transmitted bandwidth: %.1f Bytes/sec' % (1.0 * rx.overallbytes / simtime))

                mu = 350

                Wmm1 += 1.0/(mu-lam)
                print('M/M/1: %f' % Wmm1)

                Wmd1 += 1.0 * (2*mu - lam)/(2*mu*(mu - lam))

                print('M/D/1: %f' % Wmd1)

                mu1 = 1.0*B/(1500*8)
                mu2 = 1.0*B/(64*8)
                Es = 0.5 * (1.0/mu) + 0.5 * (1.0/mu)
                Es2 = 0.5 * (1.0/mu)**2 + 0.5 * (1.0/mu)**2

                Wmg1 += ((lam * Es2)/2*(1-(lam * Es))) + Es

                print('M/G/1: %f' % Wmg1)

                rho = 1.0 * lam / mu

                som = 0
                for i in range(0, k+1):
                    som += bigfloat.pow(rho, i)

                pb += (bigfloat.pow(rho, k)) / som

                pbtmp = 1.0 * (bigfloat.pow(rho, k)) / som

                lambm = (1 - pbtmp)*lam

                Wmmk += (1.0/lambm)*(
                    (rho * 1.0 / (1 - rho)) - 1.0 * ((k + 1) * bigfloat.pow(rho, (k + 1))) / (1 - bigfloat.pow(rho, (k + 1))))

                print('M/M/1/%d: %f' % (k, Wmmk))

                print('M/M/1/%d: %.2f%%' % (k, pb))

            array = array + [{'lambda': lam,
                              'queueSize': k,
                              'Loss probability': round(loss_probability/3, 5),
                              'Average delay': round(average_delay/3, 5),
                              'Transmitted bandwidth': round(trans_band/3, 5),
                              'M/M/1': round(Wmm1/3, 5),
                              'M/D/1': round(Wmd1/3, 5),
                              'M/G/1': round(Wmg1/3, 5),
                              'M/M/1/K': round(float(Wmmk)/3, 5),
                              'M/M/1/K%': round(float(100*pb)/3, 5)}]

    with open('pktSim2.json', 'w') as outfile:
        json.dump(array, outfile)

