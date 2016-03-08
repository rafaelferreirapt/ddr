import sys
import argparse
import pyshark
import math
import time
from netaddr import IPNetwork, IPAddress, IPSet
import matplotlib.pyplot as plt
from threading import Lock



"""
To use in the ubuntu server:
sudo apt-get install -y firefox tshark
bridge the wifi to a vm interface
configure as static with another ip of the network
"""

# npkts = 0

timestamp_init = 0
timestamp_interval = 0.5
timestamp_interval_graph = 5

bytes_upload = {}
idx = 0
bytes_download = {}

graph_time = 0


def pkt_callback(pkt):
    # atomic lock
    lock = Lock()
    lock.acquire()
    # atomic lock

    global scnets, ssnets, snets, cnets  # , npkts
    global graph_time, timestamp_init, timestamp_interval, timestamp_interval_graph
    global bytes_upload, idx, bytes_download

    if IPAddress(pkt.ip.src) in scnets | ssnets and IPAddress(pkt.ip.dst) in scnets | ssnets:
        timestamp = float(pkt.sniff_timestamp)
        pkt_len = bytesto(pkt.ip.len, 'm')

        if timestamp_init == 0:
            timestamp_init = timestamp
            graph_time = timestamp

        if IPAddress(pkt.ip.src) in scnets:
            # what is the network
            for network in cnets:
                if IPAddress(pkt.ip.src) in network:
                    break

            network = str(network)

            # check the interval
            interval_num = int(math.trunc((timestamp - timestamp_init) / timestamp_interval))

            if interval_num == 0:
                bytes_upload[network]["bytes"][bytes_upload[network]["idx"]] += pkt_len
            else:
                idx = bytes_upload[network]["idx"] + 1

                for i in range(idx, interval_num):
                    bytes_upload[network]["idx"] += 1
                    bytes_upload[network]["bytes"].append(0)

                if interval_num == (len(bytes_upload[network]["bytes"])-1):
                    idx = bytes_upload[network]["idx"]
                    bytes_upload[network]["bytes"][idx] += pkt_len
                else:
                    bytes_upload[network]["idx"] += 1
                    bytes_upload[network]["bytes"].append(pkt_len)

        elif IPAddress(pkt.ip.src) in ssnets:
            # what is the network
            for network in snets:
                if IPAddress(pkt.ip.src) in network:
                    break

            network = str(network)

            # check the interval
            interval_num = int(math.trunc((timestamp - timestamp_init) / timestamp_interval))

            if interval_num == 0:
                bytes_download[network]["bytes"][bytes_download[network]["idx"]] += pkt_len
            else:
                idx = bytes_download[network]["idx"] + 1

                for i in range(idx, interval_num):
                    bytes_download[network]["idx"] += 1
                    bytes_download[network]["bytes"].append(0)

                if interval_num == (len(bytes_download[network]["bytes"])-1):
                    idx = bytes_download[network]["idx"]
                    bytes_download[network]["bytes"][idx] += pkt_len
                else:
                    bytes_download[network]["idx"] += 1
                    bytes_download[network]["bytes"].append(pkt_len)

        # check the intervals
        max_idx = 0

        for cnet in cnets:
            if max_idx < bytes_upload[str(cnet)]["idx"]:
                max_idx = bytes_upload[str(cnet)]["idx"]

        for snet in snets:
            if max_idx < bytes_download[str(snet)]["idx"]:
                max_idx = bytes_download[str(snet)]["idx"]

        # interval append
        for cnet in cnets:
            idx = bytes_upload[str(cnet)]["idx"] + 1
            for i in range(idx, max_idx+1):
                bytes_upload[str(cnet)]["idx"] += 1
                bytes_upload[str(cnet)]["bytes"].append(0)

        for snet in snets:
            idx = bytes_download[str(snet)]["idx"] + 1
            for i in range(idx, max_idx+1):
                bytes_download[str(snet)]["idx"] += 1
                bytes_download[str(snet)]["bytes"].append(0)

        # draw plots
        if math.trunc((timestamp - graph_time) / timestamp_interval_graph) > 0:
            plot_show()
            graph_time = timestamp
            print bytes_upload
            print bytes_download

        # npkts = npkts + 1
        # unlock
        lock.release()
        # now it's safe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interface', nargs='?', required=True, help='capture interface')
    parser.add_argument('-c', '--cnet', nargs='+', required=True, help='client network(s)')
    parser.add_argument('-s', '--snet', nargs='+', required=True, help='service network(s)')
    parser.add_argument('-t', '--tcpport', nargs='?', help='service TCP port (or range)')
    parser.add_argument('-u', '--udpport', nargs='?', help='service UDP port (or range)')
    args = parser.parse_args()

    plt.ioff()
    plt.ion()

    global scnets, cnets, snets

    cnets = []
    for n in args.cnet:
        try:
            nn = IPNetwork(n)
            cnets.append(nn)
        except:
            print('%s is not a network prefix' % n)
    print(cnets)
    if len(cnets) == 0:
        print("No valid client network prefixes.")
        sys.exit()

    scnets = IPSet(cnets)

    snets = []
    for n in args.snet:
        try:
            nn = IPNetwork(n)
            snets.append(nn)
        except:
            print('%s is not a network prefix' % n)
    print(snets)
    if len(snets) == 0:
        print("No valid service network prefixes.")
        sys.exit()

    global ssnets
    ssnets = IPSet(snets)

    if args.udpport is not None:
        cfilter = 'udp portrange ' + args.udpport
    elif args.tcpport is not None:
        cfilter = 'tcp portrange ' + args.tcpport
    else:
        cfilter = 'ip'

    cint = args.interface
    print('Filter: %s on %s' % (cfilter, cint))
    try:
        # fill the dictionary
        for cnet in cnets:
            bytes_upload[str(cnet)] = {"bytes": [0], "idx": 0}
        for snet in snets:
            bytes_download[str(snet)] = {"bytes": [0], "idx": 0}
        plot_show()
        capture = pyshark.LiveCapture(interface=cint, bpf_filter=cfilter)
        capture.apply_on_packets(pkt_callback)
    except KeyboardInterrupt:
        pass
        # global npkts
        # print('\n%d packets captured! Done!\n' % npkts)


def plot_show():
    global scnets

    # plt
    plt.figure(1)
    plt.gcf().clear()
    plt.show()

    plt.xlabel("Time (s)")
    plt.ylabel("Mbytes")
    plt.grid(True)

    net = None

    for cnet in cnets:
        net = cnet
        break

    time_x = [math.trunc(i * timestamp_interval) for i in range(0, len(bytes_upload[str(net)]["bytes"]))]

    for cnet in snets:
        net = cnet
        break
    time_y = [math.trunc(i * timestamp_interval) for i in range(0, len(bytes_download[str(net)]["bytes"]))]

    for cnet in cnets:
        plt.plot(time_x, bytes_upload[str(cnet)]["bytes"], label=str(cnet) + " upload")
    for snet in snets:
        plt.plot(time_y, bytes_download[str(snet)]["bytes"], label=str(snet) + " download")

    plt.legend(bbox_to_anchor=(1, 1), bbox_transform=plt.gcf().transFigure)
    plt.draw()


# https://gist.github.com/shawnbutts/3906915
def bytesto(bytes, to, bsize=1024):
    a = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}
    r = float(bytes)
    for i in range(a[to]):
        r /= bsize

    return r


if __name__ == '__main__':
    main()
