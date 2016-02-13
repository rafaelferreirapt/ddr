from snimpy import mib
import time
import json
import sys

from snimpy.manager import Manager as M
from snimpy.manager import load
import re
import argparse
import matplotlib.pyplot as plt


def ip_from_octet_string(t, s):
    if t == 1 or t == 3:  # IPv4 global, non-global
        return '.'.join(['%d' % ord(x) for x in s])
    elif t == 2 or t == 4:  # IPv6 global, non-global
        a = ':'.join(['%02X%02X' % (ord(s[i]), ord(s[i + 1])) for i in range(0, 16, 2)])
        return re.sub(':{1,}:', '::', re.sub(':0*', ':', a))


def main():
    mib.path(mib.path() + ":/usr/share/mibs/cisco")
    load("SNMPv2-MIB")
    load("IF-MIB")
    load("IP-MIB")
    load("RFC1213-MIB")
    load("CISCO-QUEUE-MIB")
    # Requires MIB RFC-1212 (add to /usr/share/mibs/ietf/)

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--router', nargs='?', required=True, help='address of router to monitor')
    parser.add_argument('-s', '--sinterval', type=int, help='sampling interval (seconds)', default=5)
    args = parser.parse_args()

    sys.stdout = Logger("router_" + args.router)

    print(args)

    # Creates SNMP manager for router with address args.router
    m = M(args.router, 'private', 3, secname='uDDR', authprotocol="MD5", authpassword="authpass", privprotocol="AES",
          privpassword="privpass")

    print(m.sysDescr)  # Gets sysDescr from SNMPv2-MIB

    print("##################")

    # print(m.ifDescr.items()) #Lists (order, name) interfaces in ifDescr from IF-MIB

    for i, name in m.ifDescr.items():
        print("Interface order %d: %s" % (i, name))

    print("##################")

    ifWithAddr = {}  # Stores the interfaces with IP address
    for addr, i in m.ipAddressIfIndex.items():
        if i not in ifWithAddr:
            ifWithAddr.update({i: {"ip": ip_from_octet_string(addr[0], addr[1]), "name": m.ifDescr[i]}})
        print('%s, Interface order: %d, %s' % (ip_from_octet_string(addr[0], addr[1]), i, m.ifDescr[i]))

    t = 0

    ifOutUCastPkts = {}
    ifInUCastPkts = {}
    ifOutOctets = {}
    ifInOctets = {}
    ifQstats = {}

    ## load from json
    with open('router_10.0.0.2.json') as data_file:
        content = json.load(data_file)

    ifOutUCastPkts = content["ifOutUCastPkts"]
    ifInUCastPkts = content["ifInUCastPkts"]
    ifOutOctets = content["ifOutUCastPkts"]
    ifInOctets = content["ifOutUCastPkts"]
    ifQstats = content["ifOutUCastPkts"]

    draw_plt(ifWithAddr, ifOutUCastPkts, ifInUCastPkts, ifOutOctets, ifInOctets, ifQstats)
    exit()

    try:

        while True:
            print("\n=== %d Seconds passed ===" % t)

            """
            # ifHCOutUcastPkts
            The total number of packets that higher-level protocols
            requested be transmitted, and which were not addressed to a
            multicast or broadcast address at this sub-layer, including
            those that were discarded or not sent. This object is a
            64-bit version of ifOutUcastPkts.

            Discontinuities in the value of this counter can occur at
            re-initialization of the management system, and at other
            times as indicated by the value of
            ifCounterDiscontinuityTime."
            """
            print("\n### ifOutUCastPkts")
            ifOutUCastPkts[t] = {}

            for i, pkts in m.ifHCOutUcastPkts.items():
                if i in ifWithAddr.keys():
                    if i not in ifOutUCastPkts[t]:
                        ifOutUCastPkts[t].update({i: pkts})
                    print('%s, Interface Out packets: %d' % (m.ifDescr[i], pkts))

            """
            The number of packets, delivered by this sub-layer to a
            higher (sub-)layer, which were not addressed to a multicast
            or broadcast address at this sub-layer. This object is a
            64-bit version of ifInUcastPkts.

            Discontinuities in the value of this counter can occur at
            re-initialization of the management system, and at other
            times as indicated by the value of
            ifCounterDiscontinuityTime.
            """
            print("\n### ifInUCastPkts")
            ifInUCastPkts[t] = {}

            for i, pkts in m.ifHCInUcastPkts.items():
                if i in ifWithAddr.keys():
                    if i not in ifInUCastPkts[t]:
                        ifInUCastPkts[t].update({i: pkts})
                    print('%s, Interface In packets: %d' % (m.ifDescr[i], pkts))

            """
            The total number of octets transmitted out of the
            interface, including framing characters. This object is a
            64-bit version of ifOutOctets.

            Discontinuities in the value of this counter can occur at
            re-initialization of the management system, and at other
            times as indicated by the value of
            ifCounterDiscontinuityTime.
            """
            print("\n### ifOutOctets")
            ifOutOctets[t] = {}

            for i, pkts in m.ifHCOutOctets.items():
                if i in ifWithAddr.keys():
                    if i not in ifOutOctets[t]:
                        ifOutOctets[t].update({i: pkts})
                    print('%s, Interface Out octets: %d' % (m.ifDescr[i], pkts))

            """
            The total number of octets received on the interface,
            including framing characters. This object is a 64-bit
            version of ifInOctets.

            Discontinuities in the value of this counter can occur at
            re-initialization of the management system, and at other
            times as indicated by the value of
            ifCounterDiscontinuityTime.
            """
            print("\n### ifInOctets")
            ifInOctets[t] = {}

            for i, pkts in m.ifHCInOctets.items():
                if i in ifWithAddr.keys():
                    if i not in ifInOctets[t]:
                        ifInOctets[t].update({i: pkts})
                    print('%s, Interface In octets: %d' % (m.ifDescr[i], pkts))

            """
            The number of messages in the sub-queue.
            """
            print("\n### ifQstats")
            ifQstats[t] = {}

            for (i, u), pkts in m.cQStatsDepth.items():
                if i in ifWithAddr.keys():
                    if i not in ifQstats[t]:
                        ifQstats[t].update({i: pkts})
                    print('%s, Interface Queue Size: %d' % (m.ifDescr[i], pkts))

            time.sleep(args.sinterval)
            t += args.sinterval

    except KeyboardInterrupt:
        print "Finished after %d seconds..." % t
        json_save(args, ifWithAddr, ifOutUCastPkts, ifInUCastPkts, ifOutOctets, ifInOctets, ifQstats)
        draw_plt(ifWithAddr, ifOutUCastPkts, ifInUCastPkts, ifOutOctets, ifInOctets, ifQstats)
        sys.stdout.close()


def draw_plt(ifWithAddr, ifOutUCastPkts, ifInUCastPkts, ifOutOctets, ifInOctets, ifQstats):
    plt.ion()

    for i, details in ifWithAddr.items():
        fig = plt.figure(i, figsize=(16, 10), dpi=80)
        fig.canvas.set_window_title(str(details["name"]) + ' ' + str(details["ip"]))
        fig.subplots_adjust(wspace=0.23)

        # ifOutUCastPkts
        xitems = []
        yitems = []

        for time, value in ifOutUCastPkts.items():
            if str(i) in value:
                xitems.append(int(time))
                yitems.append(int(value[str(i)]))

        plt.subplot(231)
        plt.plot(xitems, yitems)
        plt.title("Interface out")
        plt.xlabel("time (s)")
        plt.ylabel("Unicast packets")
        plt.grid(True)

        # ifInUCastPkts
        plt.subplot(232)

        xitems = []
        yitems = []

        for time, value in ifInUCastPkts.items():
            if str(i) in value:
                xitems.append(int(time))
                yitems.append(int(value[str(i)]))

        plt.plot(xitems, yitems)
        plt.title("Interface in")
        plt.ylabel("Unicast packets")
        plt.xlabel("time (s)")
        plt.grid(True)

        # ifOutOctets
        plt.subplot(233)

        xitems = []
        yitems = []

        for time, value in ifOutOctets.items():
            if str(i) in value:
                xitems.append(int(time))
                yitems.append(int(value[str(i)]))

        plt.plot(xitems, yitems)
        plt.title("Number of bytes transmitted")
        plt.ylabel("Number of bytes")
        plt.xlabel("time (s)")
        plt.grid(True)

        # ifInOctets
        plt.subplot(234)

        xitems = []
        yitems = []

        for time, value in ifInOctets.items():
            if str(i) in value:
                xitems.append(int(time))
                yitems.append(int(value[str(i)]))

        plt.plot(xitems, yitems)
        plt.title("Number of bytes received")
        plt.ylabel("Number of bytes")
        plt.xlabel("time (s)")
        plt.grid(True)
        plt.draw()

        # ifQstats
        plt.subplot(235)

        xitems = []
        yitems = []

        for time, value in ifQstats.items():
            if str(i) in value:
                xitems.append(int(time))
                yitems.append(int(value[str(i)]))

        plt.plot(xitems, yitems)
        plt.title("The number of messages in the sub-queue.")
        plt.ylabel("Number of messages")
        plt.xlabel("time (s)")
        plt.grid(True)
        plt.draw()

    while True:
        continue


def json_save(args, ifWithAddr, ifOutUCastPkts, ifInUCastPkts, ifOutOctets, ifInOctets, ifQstats):
    save_object = {"ifWithAddr": ifWithAddr,
                   "ifOutUCastPkts": ifOutUCastPkts,
                   "ifInUCastPkts": ifInUCastPkts,
                   "ifOutOctets": ifOutOctets,
                   "ifInOctets": ifInOctets,
                   "ifQstats": ifQstats}

    with open("router_" + args.router + ".json", 'w') as outfile:
        json.dump(save_object, outfile)


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