import simpy
import numpy as np
from scipy.misc import factorial
import sys
import matplotlib.pyplot as plt


class NodeStats:
    """
        Node stats recording
        bw: Link bandwidth
    """

    def __init__(self, bw):
        self.vcs_total = 0
        self.vcs_acc = 0
        self.vcs_blk = 0
        self.bw = bw
        self.available_bw = bw
        self.lastloadchange = 0
        self.loadint = 0


def wait_for_enter():
    if sys.version_info[0] == 2:
        raw_input("Press ENTER to continue.")
    else:
        input("Press ENTER to continue.")


def vc_generator(env, av_rate, av_duration, b, stats):
    """
    VC generator
    env: SimPy environment
    av_rate: Average VC requests rate
    av_duration: Average VC duration
    b: VC required bandwidth
    stats: Node stats recording (NodeStats class)
    """
    while True:
        yield env.timeout(np.random.exponential(1.0 / av_rate))
        # yield, passa o controlo para o env, e fica a espera. do tempo atual, passado um timeout, ira rechamar
        # o processo e continuara este processo
        stats.vcs_total += 1
        if stats.available_bw >= b:
            stats.vcs_acc += 1
            stats.loadint += (1.0 / stats.bw) * (stats.bw - stats.available_bw) * (
                env.now - stats.lastloadchange)  # area
            stats.lastloadchange = env.now  # ultima mudanca de carga
            stats.available_bw -= b  # subtrair os recursos que estao disponiveis agora
            # print("time %f: VC %d started" % (env.now, stats.vcs_total))  # print a dizer que chegou
            env.process(
                vc(env, stats.vcs_total, av_duration, b, stats))  # processo que ira dizer quando a chamada ira terminar
        else:
            stats.vcs_blk += 1
            # print("time %f: VC %d blocked" % (env.now, stats.vcs_total))


def vc(env, id, av_duration, b, stats):
    """
    VC object
    env: SimPy environment
    id: VC identifier
    av_duration: Average VC duration
    b: VC required bandwidth
    stats: Global stats recording (NodeStats class)
    """
    yield env.timeout(np.random.exponential(av_duration))  # calcula a duracao da chamada
    stats.loadint += (1.0 / stats.bw) * (stats.bw - stats.available_bw) * (
        env.now - stats.lastloadchange)  # a mudanca da chamada
    stats.lastloadchange = env.now  # mudanca de carga
    stats.available_bw += b  # libertar memoria dos recursos que estavam alocados a chamada
    # print("time %f: VC %d ended" % (env.now, id))


lambdas = [1, 1.5, 2, 2.5, 3]  # taxa media de chegada dos pedidos
invmus = [2, 4, 6, 8, 10]  # duracao media das chamadas
Bs = [16, 24, 32]  # capacidade de recursos que o no tem
b = 2  # recursos necessarios por cada chamada
simtime = 3000

res = np.zeros((len(lambdas), len(invmus), len(Bs), 4))

for l, lamb in enumerate(lambdas):
    for j, invmu in enumerate(invmus):
        for k, B in enumerate(Bs):
            C = B / b

            stats = NodeStats(B)
            env = simpy.Environment()
            env.process(vc_generator(env, lamb, invmu, b, stats))
            env.run(simtime)

            print("---- lambda: %d, invmu: %d, B: %d, b: %d, simtime: %d ----" % (lamb, invmu, B, b, simtime))
            print("Simulated Block Probability=%f" % (1.0 * stats.vcs_blk / stats.vcs_total))
            print("Simulated Average Link Load=%.2f%%" % (100.0 * stats.loadint / simtime))

            rho = lamb * invmu
            i = np.arange(0, C + 1)
            blkp = (np.power(1.0 * rho, C) / factorial(C)) / np.sum(np.power(1.0 * rho, i) / factorial(i))

            print("Theoretical Block Probability=%f" % (blkp))

            i1 = np.arange(1, C + 1)
            linkload = (1.0 / C) * np.sum(np.power(1.0 * rho, i1) / factorial(i1 - 1)) / np.sum(
                np.power(1.0 * rho, i) / factorial(i))

            print("Theoretical Average Link Load=%.2f%%" % (100 * linkload))

            res[l, j, k, :] = [(1.0 * stats.vcs_blk / stats.vcs_total), (100.0 * stats.loadint / simtime), blkp,
                               (100 * linkload)]

# now plot

plt.ion()

for k, B in enumerate(Bs):
    plt.figure(k+1)
    plt.suptitle("VC Bw=2Mbits/sec; Link Bw="+str(B)+"Mbits/sec")

    for j, invmu in enumerate(invmus):
        plt.subplot(1, 2, 1)
        plt.plot(res[:, j, k, 0], label="1/$\mu$=" + str(invmu))
        plt.plot(res[:, j, k, 2], ls="dotted", c="k")
        plt.title("Block Probability")

        plt.subplot(1, 2, 2)
        plt.plot(res[:, j, k, 1], label="1/$\mu$=" + str(invmu))
        plt.plot(res[:, j, k, 3], ls="dotted", c="k")
        plt.title("Average link load")

    plt.legend(loc='upper center', bbox_to_anchor=(0, -0.05),
               fancybox=True, shadow=True, ncol=3)

    plt.savefig('graph'+str(k+1)+'.png', bbox_inches='tight')


wait_for_enter()