import sys
import argparse
import pyshark
from netaddr import IPNetwork, IPAddress, IPSet
import matplotlib.pyplot as plt
from threading import Lock

# npkts = 0

timestamp_init = 0
timestamp_interval = 0.1

bytes_upload = [0]
bytes_upload_idx = 0
bytes_download = [0]
bytes_download_idx = 0

graph_time = 0
graph_interval = 0.5


def pkt_callback(pkt):
    # atomic lock
    lock = Lock()
    lock.acquire()
    # atomic lock

    global scnets, ssnets#, npkts
    global graph_time, graph_interval, timestamp_init, timestamp_interval
    global bytes_upload_idx, bytes_upload, bytes_download_idx, bytes_download

    if IPAddress(pkt.ip.src) in scnets | ssnets and IPAddress(pkt.ip.dst) in scnets | ssnets:
        timestamp = float(pkt.sniff_timestamp)
        pkt_len = int(pkt.ip.len)

        if timestamp_init == 0:
            timestamp_init = timestamp
            graph_time = timestamp

        if IPAddress(pkt.ip.src) in scnets:
            # check the interval
            interval_num = int(round(((timestamp - timestamp_init) / timestamp_interval), 0))

            if interval_num == 0:
                bytes_upload[bytes_upload_idx] += pkt_len
            else:
                for i in range(bytes_upload_idx + 1, interval_num):
                    bytes_upload.append(0)

                bytes_upload_idx = interval_num
                bytes_upload.append(pkt_len)

        # elif IPAddress(pkt.ip.src) in ssnets:
            # check the interval
            # bytes_download[bytes_upload_idx] += pkt_len

        # draw plots
        #if round(((timestamp - graph_time) / graph_interval), 0) > 0:
        plt.plot([round(i * timestamp_interval, 2) for i in range(0, len(bytes_upload))], bytes_upload)
        # graph_time = timestamp

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
        # plt
        plt.ion()
        plt.title("YouTube")
        plt.xlabel("time (s)")
        plt.ylabel("Up/Down Mbytes")
        plt.grid(True)
        plt.show()

        while True:
            continue

        capture = pyshark.LiveCapture(interface=cint, bpf_filter=cfilter)
        capture.apply_on_packets(pkt_callback)
    except KeyboardInterrupt:
        pass
        # global npkts
        # print('\n%d packets captured! Done!\n' % npkts)


if __name__ == '__main__':
    main()
