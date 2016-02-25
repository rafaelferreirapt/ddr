
from snimpy.manager import Manager as M
from snimpy.manager import load
from snimpy import mib
import time
import re
import argparse
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import warnings
import matplotlib.cbook

def IPfromOctetString(t,s):
    if t==1 or t==3:    #IPv4 global, non-global
        return '.'.join(['%d' % ord(x) for x in s])
    elif t==2 or t==4:  #IPv6 global, non-global
        a=':'.join(['%02X%02X' % (ord(s[i]),ord(s[i+1])) for i in range(0,16,2)])
        return re.sub(':{1,}:','::',re.sub(':0*',':',a))

def main():
    mib.path(mib.path()+":/usr/share/mibs/cisco")
    load("SNMPv2-MIB")
    load("IF-MIB")
    load("IP-MIB")
    load("RFC1213-MIB")
    load("CISCO-QUEUE-MIB")
    #Requires MIB RFC-1212 (add to /usr/share/mibs/ietf/)

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--router', nargs='?',required=True, help='address of router to monitor')
    parser.add_argument('-s', '--sinterval', type=int, help='sampling interval (seconds)',default=5)
    args=parser.parse_args()

    sys.stdout = Logger("router_" + args.router)

    #Creates SNMP manager for router with address args.router
    m=M(args.router,'private',3, secname='uDDR',authprotocol="MD5", authpassword="authpass",privprotocol="AES", privpassword="privpass")

    print(m.sysDescr)   #Gets sysDescr from SNMPv2-MIB

    ifWithAddr={}   #Stores (order, first adr.) of all interfaces
    for addr, i in m.ipAddressIfIndex.items():
        if not i in ifWithAddr:
            ifWithAddr.update({i:IPfromOctetString(addr[0],addr[1])})


    t = 0

    fig = plt.figure(num=None, figsize=(10, 7.5), dpi=80)
    plt.subplots_adjust(wspace=0.25)
    plt.subplots_adjust(hspace=0.25)
    plt.ion()

    try:
        inPkts = {}
        inPktsDiference = {}
        outPkts = {}
        outPktsDiference = {}
        inOcts = {}
        inOctsDiference = {}
        outOcts = {}
        outOctsDiference = {}
        colors = {}
        colormap = ['r.-','y.-','g.-','b.-','m.-']
        counter = 0
        patches=[]
        for i, name in m.ifDescr.items():
            if i in ifWithAddr:
                inPkts.update({name:[]})
                inPktsDiference.update({name:[]})
                outPkts.update({name:[]})
                outPktsDiference.update({name:[]})
                inOcts.update({name:[]})
                inOctsDiference.update({name:[]})
                outOcts.update({name:[]})
                outOctsDiference.update({name:[]})

                colors.update({name:colormap[counter]})
                counter +=1
                if counter >= len(colormap):
                    counter =0

        counter = 0
        while True:
            ifOutUCastPkts={} #Stores (order, OutPkts) of all interfaces
            for i, pkts in m.ifHCOutUcastPkts.items():
                if i in ifWithAddr.keys():
                    if not i in ifOutUCastPkts:
                        ifOutUCastPkts.update({i:pkts})

            ifInUCastPkts={} #Stores (order, InPkts) of all interfaces
            for i, pkts in m.ifHCInUcastPkts.items():
                if i in ifWithAddr.keys():
                    if not i in ifInUCastPkts:
                        ifInUCastPkts.update({i:pkts})

            ifOutOctets={} #Stores (order, OutOctets) of all interfaces
            for i, pkts in m.ifHCOutOctets.items():
                if i in ifWithAddr.keys():
                    if not i in ifOutOctets:
                        ifOutOctets.update({i:pkts})

            ifInOctets={} #Stores (order, InOctets) of all interfaces
            for i, pkts in m.ifHCInOctets.items():
                if i in ifWithAddr.keys():
                    if not i in ifInOctets:
                        ifInOctets.update({i:pkts})

            ifQstats={} #Stores (order, queue_size) of all interfaces
            for (i,u),pkts in m.cQStatsDepth.items():
                if i in ifWithAddr.keys():
                    if not i in ifQstats:
                        ifQstats.update({i:pkts})

            x = np.arange(0, t+args.sinterval, 5)

            order = []

            aux = 0

            print("=== %d Seconds passed ===" % t)
            for i, name in m.ifDescr.items():
                if i in ifWithAddr:

                    print("%s, %s \t pkts[in/out][%s/%s] \t octets[in/out][%s/%s] \t queue[%s]" % (ifWithAddr[i], name, ifInUCastPkts[i], ifOutUCastPkts[i], ifInOctets[i], ifOutOctets[i], ifQstats[i]))
                    order.append(name)

                    #Plot in Packets
                    plt.subplot(2, 2, 1)
                    plt.title('In Packets')
                    plt.ylabel('Packets')
                    inPkts[name] += [ifInUCastPkts[i]]
                    inPktsDiference[name] += [ifInUCastPkts[i]]
                    if(counter != 0):
                        if counter==1:
                            inPktsDiference[name][1] = inPkts[name][1]-inPkts[name][0]
                            inPktsDiference[name][0] = 0
                        else:
                            inPktsDiference[name][counter] = inPkts[name][counter]-inPkts[name][counter-1]

                        plt.plot(x, inPktsDiference[name], colors[name])
                    else:
                        plt.plot(x, 0, colors[name])

                    #Plot out Packets
                    plt.subplot(2, 2, 2)
                    plt.title('Out Packets')
                    outPkts[name] += [ifOutUCastPkts[i]]
                    outPktsDiference[name] += [ifOutUCastPkts[i]]
                    if(counter != 0):
                        if counter==1:
                            outPktsDiference[name][1] = outPkts[name][1]-outPkts[name][0]
                            outPktsDiference[name][0] = 0
                        else:
                            outPktsDiference[name][counter] = outPkts[name][counter]-outPkts[name][counter-1]

                        plt.plot(x, outPktsDiference[name], colors[name])
                    else:
                        plt.plot(x, 0, colors[name])

                    #Plot in Octets
                    plt.subplot(2, 2, 3)
                    plt.title('In Octets')
                    plt.xlabel('Time (s)')
                    plt.ylabel('Octets')
                    inOcts[name] += [ifInOctets[i]]
                    inOctsDiference[name] += [ifInOctets[i]]
                    if(counter != 0):
                        if counter==1:
                            inOctsDiference[name][1] = inOcts[name][1]-inOcts[name][0]
                            inOctsDiference[name][0] = 0
                        else:
                            inOctsDiference[name][counter] = inOcts[name][counter]-inOcts[name][counter-1]

                        plt.plot(x, inOctsDiference[name], colors[name])
                    else:
                        plt.plot(x, 0, colors[name])

                    #Plot out Octets
                    plt.subplot(2, 2, 0)
                    plt.title('Out Octets')
                    plt.xlabel('Time (s)')
                    outOcts[name] += [ifOutOctets[i]]
                    outOctsDiference[name] += [ifOutOctets[i]]
                    if(counter != 0):
                        if counter==1:
                            outOctsDiference[name][1] = outOcts[name][1]-outOcts[name][0]
                            outOctsDiference[name][0] = 0
                        else:
                            outOctsDiference[name][counter] = outOcts[name][counter]-outOcts[name][counter-1]

                        plt.plot(x, outOctsDiference[name], colors[name])
                    else:
                        plt.plot(x, 0, colors[name])

                    aux+=1

            print("========================")
            counter+=1
            plt.subplot(2, 2, 1)
            plt.legend(order, ncol=4, loc='upper center', bbox_to_anchor=[1.1, 1.3], columnspacing=1.0, labelspacing=0.0,handletextpad=0.0, handlelength=1.5, fancybox=True, shadow=True)

            plt.draw()

            time.sleep(args.sinterval)
            t += args.sinterval


    except KeyboardInterrupt:
        print "Finished after %d seconds..." % t
        fig.savefig('output.jpg')
        sys.stdout.close()


class Logger(object):
    def __init__(self, fname):
        self.terminal = sys.stdout
        self.log = open(fname, "w+")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def close(self):
        self.log.close()


if __name__ == "__main__":
    main()