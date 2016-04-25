import simpy
import random
import numpy as np


class Packet(object):
    """
    Packet Object
    time: packet creation time/ID (float)
    size: packet size (integer)
    dst: packet destination (string) - pkt_Receiver ID
    """

    def __init__(self, time, size, dst):
        self.time = time
        self.size = size
        self.dst = dst

    def __repr__(self):
        return 'Pkt %f [%d] to %s' % (self.time, self.size, self.dst)


class Node(object):
    """
    Node Object
    env: SimPy environment
    id: Node ID (string)
    speed: Node routing speed (float, pkts/sec)
    qsize: Node input queue size (integer, number of packets, default inf)
    """

    def __init__(self, env, id, speed, qsize=np.inf):
        self.env = env
        self.id = id
        self.speed = speed
        self.qsize = qsize
        self.queue = simpy.Store(env)
        self.lost_pkts = 0
        self.out = {}  # list with obj {'dest1':[elem1,elem3],'dest2':[elem1,elem2],...}
        self.action = env.process(self.run())

    def add_conn(self, elem, dsts):
        """
        Defines node output connections to other simulation elements
        elem: Next element (object)
        dsts: list with destination(s) ID(s) accessible via elem (string or list of strings)
        """
        for d in dsts:
            if self.out.has_key(d):
                self.out[d].append(elem)
            else:
                self.out.update({d: [elem]})

    def run(self):
        while True:
            pkt = (yield self.queue.get())
            yield self.env.timeout(1.0 * pkt.size / self.speed)
            if self.out.has_key(pkt.dst):
                # random routing over all possible paths to dst
                outobj = self.out[pkt.dst][random.randint(0, len(self.out[pkt.dst]) - 1)]
                print(str(self.env.now) + ': Packet out node ' + self.id + ' - ' + str(pkt))
                outobj.put(pkt)
            else:
                print(str(self.env.now) + ': Packet lost in node ' + self.id + '- No routing path - ' + str(pkt))

    def put(self, pkt):
        if len(self.queue.items) < self.qsize:
            self.queue.put(pkt)
        else:
            self.lost_pkts += 1
            print(str(env.now) + ': Packet lost in node ' + self.id + ' queue - ' + str(pkt))


class Link(object):
    """
    Link Object
    env: SimPy environment
    id: Link ID (string)
    speed: Link transmission speed (float, bits/sec)
    qsize: Node to Link output queue size (integer, number of packets, default inf)
    """

    def __init__(self, env, id, speed, qsize=np.inf):
        self.env = env
        self.id = id
        self.speed = 1.0 * speed / 8
        self.qsize = qsize
        self.queue = simpy.Store(env)
        self.lost_pkts = 0
        self.out = None
        self.action = env.process(self.run())

    def run(self):
        while True:
            pkt = (yield self.queue.get())
            yield self.env.timeout(1.0 * pkt.size / self.speed)
            print(str(self.env.now) + ': Packet out link ' + self.id + ' - ' + str(pkt))
            self.out.put(pkt)

    def put(self, pkt):
        if len(self.queue.items) < self.qsize:
            self.queue.put(pkt)
        else:
            self.lost_pkts += 1
            print(str(self.env.now) + ': Packet lost in link ' + self.id + ' queue - ' + str(pkt))


class pkt_Sender(object):
    """
    Packet Sender
    env: SimPy environment
    id: Sender ID (string)
    rate: Packet generation rate (float, packets/sec)
    dst: List with packet destinations (list of strings, if size>1 destination is random among all possible destinations)
    """

    def __init__(self, env, id, rate, dst):
        self.env = env
        self.id = id
        self.rate = rate
        self.out = None
        self.dst = dst
        self.packets_sent = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(np.random.exponential(1.0 / self.rate))
            self.packets_sent += 1
            # size=random.randint(64,1500)
            # size=int(np.random.exponential(500))
            size = int(np.random.choice([64, 1500], 1, [.5, .5]))
            if len(self.dst) == 1:
                dst = self.dst[0]
            else:
                dst = self.dst[random.randint(0, len(self.dst) - 1)]
            pkt = Packet(self.env.now, size, dst)
            print(str(self.env.now) + ': Packet sent by ' + self.id + ' - ' + str(pkt))
            self.out.put(pkt)


class pkt_Receiver(object):
    """
    Packet Receiver
    env: SimPy environment
    id: Sender ID (string)
    """

    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.queue = simpy.Store(env)
        self.packets_recv = 0
        self.overalldelay = 0
        self.overallbytes = 0
        self.action = env.process(self.run())

    def run(self):
        while True:
            pkt = (yield self.queue.get())
            self.packets_recv += 1
            self.overalldelay += self.env.now - pkt.time
            self.overallbytes += pkt.size
            print(str(self.env.now) + ': Packet received by ' + self.id + ' - ' + str(pkt))

    def put(self, pkt):
        self.queue.put(pkt)


env = simpy.Environment()

# Sender (tx) -> Node1 -> Link -> Receiver (rx)

lamb = 600
K = 128
B = 10e9
tmp = 782  # 0.5*1500+0.5*64 bytes em media

rx = pkt_Receiver(env, 'B')
tx = pkt_Sender(env, 'A', lamb, 'B')
node1 = Node(env, 'N1', 100, K)
link = Link(env, 'L', B, np.inf)

tx.out = node1
node1.add_conn(link, 'B')
link.out = rx

print(node1.out)

simtime = 30
env.run(simtime)
print(node1.queue.items)
print('Loss probability: %.2f%%' % (100.0 * node1.lost_pkts / tx.packets_sent))
print('Average delay: %f sec' % (1.0 * rx.overalldelay / rx.packets_recv))
print('Transmitted bandwidth: %.1f Bytes/sec' % (1.0 * rx.overallbytes / simtime))

mu = B/(tmp*8)

Wmm1 = 1/(mu-lamb)
print('M/M/1: %f' % Wmm1)

Wmd1 = (2*mu - lamb)/(2*mu*(mu - lamb))

print('M/D/1: %f' % Wmd1)

mu1 = B/(1500*8)
mu2 = B/(64*8)
Es = 0.5 * (1/mu1) + 0.5 * (1/mu2)
Es2 = 0.5 * (1/mu1)**2 + 0.5 * (1/mu2)**2

Wmg1 = ((lamb * Es2)/2*(1-(lamb * Es))) + Es

print('M/G/1: %f' % Wmg1)

row = lamb/mu

som = 0
for i in range(0, K+1):
    som += row**i

pb = (row**K)/som

lambm = (1 - pb)*lamb

Wmmk = (1/lambm)*((row/(1-row)) - ((K+1) * row**(K+1))/(1-row**(K+1)))

print('M/M/1/%d: %f' % (K, Wmmk))

print('M/M/1/%d: %.2f%%' % (K, pb))

