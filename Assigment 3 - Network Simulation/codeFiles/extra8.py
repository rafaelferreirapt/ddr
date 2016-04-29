import simpy
import numpy as np
from PktSim1 import pkt_Receiver, pkt_Sender, Node, Link

env = simpy.Environment()

# Sender (tx) -> Node1 -> Link -> Receiver (rx)

lamb = 600
K = 128
B = 2e6
tmp = 782  # 0.5*1500+0.5*64 bytes em media

rx = pkt_Receiver(env, 'B')
tx = pkt_Sender(env, 'A', lamb, 'B')
node1 = Node(env, 'N1', np.inf)
link = Link(env, 'L', B, K)

tx.out = node1
node1.add_conn(link, 'B')
link.out = rx

print(node1.out)

simtime = 30
env.run(simtime)

print('Loss probability: %.2f%%' % (100.0 * link.lost_pkts / tx.packets_sent))
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

# Sender (tx) -> Node1 -> Link -> Receiver (rx)

lamb = 600
K = 128
B = 10e9
tmp = 782  # 0.5*1500+0.5*64 bytes em media

rx = pkt_Receiver(env, 'B')
tx = pkt_Sender(env, 'A', lamb, 'B')
node2 = Node(env, 'N1', 100, K)
link = Link(env, 'L', B, np.inf)

tx.out = node2
node2.add_conn(link, 'B')
link.out = rx

print(node2.out)

simtime = 30
env.run(simtime)
print(node2.queue.items)
print('Loss probability: %.2f%%' % (100.0 * node2.lost_pkts / tx.packets_sent))
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