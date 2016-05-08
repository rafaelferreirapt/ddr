import simpy
import numpy as np
from PktSim1 import pkt_Receiver, Node, Link, print_debug, Packet
import pickle
import random
from colorama import Fore, Back, Style


simtime = 0


class pkt_Sender(object):

    """
    Packet Sender
    env: SimPy environment
    id: Sender ID (string)
    rate: Packet generation rate (float, packets/sec)
    dst: List with packet destinations (list of strings, if size>1 destination is random among all possible destinations)
    """

    def __init__(self, env, id, dst, list_pkts):
        self.env = env
        self.id = id
        self.out = None
        self.dst = dst
        self.packets_sent = 0
        self.list_pkts = list_pkts
        self.action = env.process(self.run())

    def run(self):
        global simtime

        for pkt_l in self.list_pkts:
            if pkt_l["number_of_packets"] == 0:
                time = pkt_l["time"]
                simtime += time

                yield self.env.timeout(time)
            else:
                for i in range(0, pkt_l["number_of_packets"]):
                    time = pkt_l["time"]
                    simtime += time

                    yield self.env.timeout(time)

                    self.packets_sent += 1
                    # size=random.randint(64,1500)
                    # size=int(np.random.exponential(500))
                    size = pkt_l["size"]

                    if len(self.dst) == 1:
                        dst = self.dst[0]
                    else:
                        dst = self.dst[random.randint(0, len(self.dst) - 1)]

                    pkt = Packet(self.env.now, size, dst)
                    print_debug(str(self.env.now) + ': Packet sent by ' + self.id + ' - ' + str(pkt))
                    self.out.put(pkt)

        self.env.exit()

if __name__ == '__main__':
    print Fore.BLUE + Style.BRIGHT + "NODE 1" + Style.RESET_ALL

    # time generated, see extra8_generate.py

    with open("time_gen.p", 'rb') as f:
        time_packets = pickle.load(f)

    env = simpy.Environment()

    # Sender (tx) -> Node1 -> Link -> Receiver (rx)

    lamb = 600
    K = 128
    B = 2e6
    tmp = 782  # 0.5*1500+0.5*64 bytes em media

    rx = pkt_Receiver(env, 'B')
    tx = pkt_Sender(env, 'A', 'B', time_packets)
    node1 = Node(env, 'N1', np.inf)
    link = Link(env, 'L', B, K)

    tx.out = node1
    node1.add_conn(link, 'B')
    link.out = rx

    env.run()

    print((Fore.LIGHTBLUE_EX + "Loss probability:" + Fore.GREEN + " %.2f%%" + Style.RESET_ALL) % (100.0 * link.lost_pkts / tx.packets_sent))
    print((Fore.LIGHTBLUE_EX + 'Average delay:' + Fore.GREEN + ' %f sec' + Style.RESET_ALL) % (1.0 * rx.overalldelay / rx.packets_recv))
    print((Fore.LIGHTBLUE_EX + 'Transmitted bandwidth:' + Fore.GREEN + ' %.1f Bytes/sec' + Style.RESET_ALL) % (1.0 * rx.overallbytes / simtime))

    mu = B/(tmp*8)

    Wmm1 = 1/(mu-lamb)
    print((Fore.LIGHTBLUE_EX + 'M/M/1:' + Fore.GREEN + ' %f' + Style.RESET_ALL) % Wmm1)

    Wmd1 = (2*mu - lamb)/(2*mu*(mu - lamb))

    print((Fore.LIGHTBLUE_EX + 'M/D/1:' + Fore.GREEN + ' %f' + Style.RESET_ALL) % Wmd1)

    mu1 = B/(1500*8)
    mu2 = B/(64*8)
    Es = 0.5 * (1/mu1) + 0.5 * (1/mu2)
    Es2 = 0.5 * (1/mu1)**2 + 0.5 * (1/mu2)**2

    Wmg1 = ((lamb * Es2)/2*(1-(lamb * Es))) + Es

    print((Fore.LIGHTBLUE_EX + 'M/G/1:' + Fore.GREEN + ' %f' + Style.RESET_ALL) % Wmg1)

    row = lamb/mu

    som = 0
    for i in range(0, K+1):
        som += row**i

    pb = (row**K)/som

    lambm = (1 - pb)*lamb

    Wmmk = (1/lambm)*((row/(1-row)) - ((K+1) * row**(K+1))/(1-row**(K+1)))

    print((Fore.LIGHTBLUE_EX + 'M/M/1/%d:' + Fore.GREEN + ' %f' + Style.RESET_ALL) % (K, Wmmk))

    print((Fore.LIGHTBLUE_EX + 'M/M/1/%d:' + Fore.GREEN + ' %.2f%%' + Style.RESET_ALL) % (K, pb))
