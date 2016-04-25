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

    def __init__(self, bw, reserved, numberServices):
        self.vcs_total = np.zeros(2)
        self.vcs_acc = np.zeros(2)
        self.vcs_blk = np.zeros(2)
        self.bw = bw
        self.reserved = np.array(reserved)
        self.bwres = np.sum(reserved)
        self.available_bw = bw
        self.lastloadchange = 0
        self.loadint = 0


def wait_for_enter():
    if sys.version_info[0] == 2:
        raw_input("Press ENTER to continue.")
    else:
        input("Press ENTER to continue.")


def vc_generator(env, id, av_rate, av_duration, b, stats):
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
        stats.vcs_total[id - 1] += 1
        if stats.available_bw >= b + stats.bwres - stats.reserved[id - 1]:
            stats.vcs_acc[id - 1] += 1
            stats.loadint += (1.0 / stats.bw) * (stats.bw - stats.available_bw) * (
                env.now - stats.lastloadchange)  # area
            stats.lastloadchange = env.now  # ultima mudanca de carga
            stats.available_bw -= b  # subtrair os recursos que estao disponiveis agora
            # print("time %f: VC %d started" % (env.now, stats.vcs_total))  # print a dizer que chegou
            env.process(
                vc(env, stats.vcs_total, av_duration, b, stats))  # processo que ira dizer quando a chamada ira terminar
        else:
            stats.vcs_blk[id - 1] += 1
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


N = 2
lambdastandard = [1, 2, 3, 4, 5]  # taxa media de chegada dos pedidos
lambdaspecial = [1, 1.5, 2, 2.5, 3]  # taxa media de chegada dos pedidos

invmus = [2, 4, 6, 8, 10]  # duracao media das chamadas
Bs = [16, 24, 32]  # capacidade de recursos que o no tem
R = [0, 4, 8, 16]
bstandard = 2  # recursos necessarios por cada chamada
bspecial = 4  # recursos necessarios por cada chamada

simtime = 3000

res = np.zeros((len(lambdastandard), len(invmus), len(Bs), 4))

'''
stats = NodeStats(32, R, N)
env = simpy.Environment()
env.process(vc_generator(env, 1, lambdastandard[1], invmus[1], bstandard, stats))
env.process(vc_generator(env, 2, lambdaspecial[0], invmus[1], bspecial, stats))
env.run(simtime)

for id in range(1, 3):
    print("Simulated Block Probability %d=%f" % (id, 1.0 * stats.vcs_blk[id-1] / stats.vcs_total[id-1]))

print("Simulated Average Link Load=%.2f%%" % (100.0 * stats.loadint / simtime))
'''

for l, lambstan in enumerate(lambdastandard):
    for a, lambspe in enumerate(lambdaspecial):

        for j, invmu in enumerate(invmus):
            for k, B in enumerate(Bs):
                C1 = B / bstandard
                C2 = B / bspecial

                stats = NodeStats(B, R, N)
                env = simpy.Environment()
                env.process(vc_generator(env, 1, lambstan, invmu, bstandard, stats))
                env.process(vc_generator(env, 2, lambspe, invmu, bspecial, stats))
                # env.process(vc_generator(env, lamb, invmu, b, stats))
                env.run(simtime)

                print("---- lambdaStandard: %d, lambdaSpecial: %.1f, invmu: %d, B: %d, bStandard: %d, bSpecial: %d, simtime: %d ----" % (
                lambstan, lambspe, invmu, B, bstandard, bspecial, simtime))

                for id in range(1, N + 1):
                    print(
                    "Simulated Block Probability %d=%f" % (id, 1.0 * stats.vcs_blk[id - 1] / stats.vcs_total[id - 1]))

                print("Simulated Average Link Load=%.2f%%" % (100.0 * stats.loadint / simtime))

                rho1 = lambstan * invmu
                i1 = np.arange(0, C1 + 1)
                blkp1 = (np.power(1.0 * rho1, C1) / factorial(C1)) / np.sum(np.power(1.0 * rho1, i1) / factorial(i1))
                print("Theoretical Block Probability %d=%f" % (1, blkp1))

                rho2 = lambspe * invmu
                i2 = np.arange(0, C2 + 1)
                blkp2 = (np.power(1.0 * rho2, C2) / factorial(C2)) / np.sum(np.power(1.0 * rho2, i2) / factorial(i2))
                print("Theoretical Block Probability %d=%f" % (2, blkp2))

                i3 = np.arange(1, C1 + 1)
                linkload1 = (1.0 / C1) * np.sum(np.power(1.0 * rho1, i3) / factorial(i3 - 1)) / np.sum(
                    np.power(1.0 * rho1, i1) / factorial(i1))

                i4 = np.arange(1, C2 + 1)
                linkload2 = (1.0 / C2) * np.sum(np.power(1.0 * rho2, i4) / factorial(i4 - 1)) / np.sum(
                    np.power(1.0 * rho2, i2) / factorial(i2))

                print("Theoretical Average Link Load %d=%.2f%%" % (1, 100 * linkload1))
                print("Theoretical Average Link Load %d=%.2f%%" % (2, 100 * linkload2))


'''
# now plot

plt.ion()

for k, B in enumerate(Bs):
    plt.figure(k+1)
    plt.suptitle("VC Bw=2Mbits/sec; Link Bw="+str(B)+"Mbits/sec")

    for j, invmu in enumerate(invmus):
        plt.subplot(1, 2, 1)
        plt.plot(resStandard[:, j, k, 0], label="1/$\mu$=" + str(invmu))
        plt.plot(resStandard[:, j, k, 2], ls="dotted", c="k")
        plt.title("Block Probability")

        plt.subplot(1, 2, 2)
        plt.plot(resStandard[:, j, k, 1], label="1/$\mu$=" + str(invmu))
        plt.plot(resStandard[:, j, k, 3], ls="dotted", c="k")
        plt.title("Average link load")

    plt.legend(loc='upper center', bbox_to_anchor=(0, -0.05),
               fancybox=True, shadow=True, ncol=3)

    plt.savefig('graph'+str(k+1)+'.png', bbox_inches='tight')

'''
wait_for_enter()
