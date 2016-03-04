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
timestamp_interval = 20

bytes_upload = {}
idx = 0
bytes_download = {}

graph_time = 0


def pkt_callback(pkt):
    # atomic lock
    lock = Lock()
    lock.acquire()
    # atomic lock

    global scnets, ssnets  # , npkts
    global graph_time, timestamp_init, timestamp_interval
    global bytes_upload, idx, bytes_download

    if IPAddress(pkt.ip.src) in scnets | ssnets and IPAddress(pkt.ip.dst) in scnets | ssnets:
        timestamp = float(pkt.sniff_timestamp)
        pkt_len = bytesto(pkt.ip.len, 'm')

        if timestamp_init == 0:
            timestamp_init = timestamp
            graph_time = timestamp

        if IPAddress(pkt.ip.src) in scnets:
            # check the interval
            interval_num = int(math.trunc((timestamp - timestamp_init) / timestamp_interval))

            if interval_num == 0:
                bytes_upload[pkt.ip.src]["bytes"][bytes_upload[pkt.ip.src]["idx"]] += pkt_len
            else:
                for i in range(bytes_upload[pkt.ip.src]["idx"] + 1, interval_num):
                    bytes_upload[pkt.ip.src]["bytes"].append(0)

                if interval_num == (len(bytes_upload)-1):
                    bytes_upload[bytes_upload[pkt.ip.src]["idx"]] += pkt_len
                else:
                    bytes_upload[pkt.ip.src]["idx"] = interval_num
                    bytes_upload[pkt.ip.src]["bytes"].append(pkt_len)

        elif IPAddress(pkt.ip.src) in ssnets:
            # check the interval
            interval_num = int(math.trunc((timestamp - timestamp_init) / timestamp_interval))

            if interval_num == 0:
                bytes_download[pkt.ip.src]["bytes"][bytes_download[pkt.ip.src]["idx"]] += pkt_len
            else:
                for i in range(bytes_download[pkt.ip.src]["idx"] + 1, interval_num):
                    bytes_download[pkt.ip.src]["bytes"].append(0)

                if interval_num == (len(bytes_download)-1):
                    bytes_download[bytes_download[pkt.ip.src]["idx"]] += pkt_len
                else:
                    bytes_download[pkt.ip.src]["idx"] = interval_num
                    bytes_download[pkt.ip.src]["bytes"].append(pkt_len)
            # bytes_download[bytes_upload_idx] += pkt_len

        # draw plots
        if math.trunc((timestamp - graph_time) / timestamp_interval) > 0:
            plot_show()
            graph_time = timestamp

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
    global scnets
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
        for cnet in scnets:
            bytes_upload[str(cnet)] = {"bytes": [0], "idx": 0}
        for snet in ssnets:
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
    plt.ioff()
    plt.ion()
    plt.gcf().clear()

    plt.xlabel("Time (s)")
    plt.ylabel("Mbytes")
    plt.grid(True)

    net = None

    for cnet in scnets:
        net = cnet
        break

    time_x = [math.trunc(i * timestamp_interval) for i in range(0, len(bytes_upload[str(net)]["bytes"]))]

    for cnet in ssnets:
        net = cnet
        break
    time_y = [math.trunc(i * timestamp_interval) for i in range(0, len(bytes_download[str(net)]["bytes"]))]

    for cnet in scnets:
        plt.plot(time_x, bytes_upload[str(cnet)]["bytes"], label=str(cnet) + " upload")
    for snet in ssnets:
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
