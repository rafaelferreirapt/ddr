import simpy
import numpy as np
# sudo apt-get install libmpfr-dev
# sudo pip install bigfloat
import bigfloat
import json
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link, Packet


# Sender (tx) -> Node1 -> Link -> Receiver (rx)

lamb = [150, 300, 450]
K = [64, 96, 128, 10000]
B = 10e9
tmp = 782  # 0.5*1500+0.5*64 bytes em media

array = []

for lam in lamb:
    for k in K:
        env = simpy.Environment()

        rx = pkt_Receiver(env, 'B')
        tx = pkt_Sender(env, 'A', lam, 'B')
        node1 = Node(env, 'N1', 350, k)
        link = Link(env, 'L', B, np.inf)

        tx.out = node1
        node1.add_conn(link, 'B')
        link.out = rx

        simtime = 30
        env.run(simtime)
        print("---- lambda: %d, queue size: %d, B: %d, simtime: %d ----" % (lam, k, B, simtime))
        print('Loss probability: %.2f%%' % (100.0 * node1.lost_pkts / tx.packets_sent))
        print('Average delay: %f sec' % (1.0 * rx.overalldelay / rx.packets_recv))
        print('Transmitted bandwidth: %.1f Bytes/sec' % (1.0 * rx.overallbytes / simtime))

        mu = 350

        Wmm1 = 1.0/(mu-lam)
        print('M/M/1: %f' % Wmm1)

        Wmd1 = 1.0 * (2*mu - lam)/(2*mu*(mu - lam))

        print('M/D/1: %f' % Wmd1)

        mu1 = 1.0*B/(1500*8)
        mu2 = 1.0*B/(64*8)
        Es = 0.5 * (1.0/mu) + 0.5 * (1.0/mu)
        Es2 = 0.5 * (1.0/mu)**2 + 0.5 * (1.0/mu)**2

        Wmg1 = ((lam * Es2)/2*(1-(lam * Es))) + Es

        print('M/G/1: %f' % Wmg1)

        row = 1.0*lam/mu

        som = 0
        for i in range(0, k+1):
            som += bigfloat.pow(row, i)

        pb = 1.0*(bigfloat.pow(row, k))/som

        lambm = (1 - pb)*lam

        Wmmk = (1.0/lambm)*(
            (row*1.0/(1-row)) - 1.0 * ((k+1) * bigfloat.pow(row, (k + 1)))/(1-bigfloat.pow(row, (k + 1))))

        print('M/M/1/%d: %f' % (k, Wmmk))

        print('M/M/1/%d: %.2f%%' % (k, pb))

        array = array + [{'lambda': lam, 'queueSize': k, 'Loss probability': (100.0 * node1.lost_pkts / tx.packets_sent),
                          'Average delay': (1.0 * rx.overalldelay / rx.packets_recv),
                          'Transmitted bandwidth': (1.0 * rx.overallbytes / simtime), 'M/M/1': Wmm1, 'M/D/1': Wmd1,
                          'M/G/1': Wmg1, 'M/M/1/K': float(Wmmk), 'M/M/1/K%': float(pb)}]

with open('pktSim2.json', 'w') as outfile:
    json.dump(array, outfile)

