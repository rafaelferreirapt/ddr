import sys
import argparse
import pyshark
from netaddr import IPNetwork, IPAddress, IPSet
import matplotlib.pyplot as plt

npkts = 0

timestamp_init = 0
timestamp_interval = 0.15

bytes_upload = [0]
bytes_upload_idx = 0
bytes_download = [0]
bytes_download_idx = 0
time = [0]
last_time = 0

graph_time = 0
graph_interval = 5


def pkt_callback(pkt):
    global scnets, graph, graph_time, graph_interval
    global ssnets, timestamp_init, last_time
    global npkts, time, bytes_upload_idx, bytes_download_idx
    global timestamp_interval, bytes_download, bytes_upload

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
                for i in range(bytes_upload_idx+1, interval_num):
                    bytes_upload.append(0)
                    time.append(last_time + 0.15)
                    last_time = last_time + 0.15

                bytes_upload_idx = interval_num
                bytes_upload.append(0)
                bytes_upload[bytes_upload_idx] = pkt_len
                time.append(last_time + 0.15)
                last_time = last_time + 0.15

        elif IPAddress(pkt.ip.src) in ssnets:
            # check the interval
            bytes_download[bytes_upload_idx] += pkt_len

        # draw plots
        if round(((timestamp - graph_time) / graph_interval), 0) > 0:
            plt.ion()
            plt.plot(time, bytes_upload)
            plt.title("YouTube")
            plt.xlabel("time (s)")
            plt.ylabel("Up/Down Mbytes")
            plt.draw()

            graph_time = timestamp

        npkts = npkts + 1

        # if pkt.ip.proto == '17':
        #     print('%s: IP packet from %s to %s (UDP:%s) %s' % (
        #     pkt.sniff_timestamp, pkt.ip.src, pkt.ip.dst, pkt.udp.dstport, pkt.ip.len))
        # elif pkt.ip.proto == '6':
        #     print('%s: IP packet from %s to %s (TCP:%s) %s' % (
        #     pkt.sniff_timestamp, pkt.ip.src, pkt.ip.dst, pkt.tcp.dstport, pkt.ip.len))
        # else:
        #     print('%s: IP packet from %s to %s (other) %s' % (pkt.sniff_timestamp, pkt.ip.src, pkt.ip.dst, pkt.ip.len))


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
        capture = pyshark.LiveCapture(interface=cint, bpf_filter=cfilter)
        capture.apply_on_packets(pkt_callback)
    except KeyboardInterrupt:
        global npkts
        print('\n%d packets captured! Done!\n' % npkts)


if __name__ == '__main__':
    main()
