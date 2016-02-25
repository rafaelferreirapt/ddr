import argparse
import socket
import struct
import sys
from netaddr import IPNetwork, IPAddress, IPSet


class Table:

    TM = {}
    table_header = []
    table_left = []

    def __init__(self, nets):
        self.table_header += nets + ['other']
        self.table_left += nets + ['other']

        for ip_src in nets:
            for ip_dst in nets:
                self.TM[(str(ip_src), str(ip_dst))] = {}
                self.TM[(str(ip_src), str(ip_dst))]['flows'] = 0
                self.TM[(str(ip_src), str(ip_dst))]['packets'] = 0
                self.TM[(str(ip_src), str(ip_dst))]['bytes'] = 0

        for ip_src in nets:
            self.TM[(str(ip_src), 'other')] = {}
            self.TM[(str(ip_src), 'other')]['flows'] = 0
            self.TM[(str(ip_src), 'other')]['packets'] = 0
            self.TM[(str(ip_src), 'other')]['bytes'] = 0

        for ip_dst in nets:
            self.TM[('other', str(ip_dst))] = {}
            self.TM[('other', str(ip_dst))]['flows'] = 0
            self.TM[('other', str(ip_dst))]['packets'] = 0
            self.TM[('other', str(ip_dst))]['bytes'] = 0

        self.TM[('other', 'other')] = {}
        self.TM[('other', 'other')]['flows'] = 0
        self.TM[('other', 'other')]['packets'] = 0
        self.TM[('other', 'other')]['bytes'] = 0

    def update(self, sn, dn, packets, bts):
        stats = self.TM[sn, dn]
        stats['flows'] += 1
        stats['packets'] += packets
        stats['bytes'] += bts
        self.TM.update({(sn, dn): stats})

    def __str__(self):
        header_str = ('%14s ' % '')
        for header in self.table_header:
            header_str += ('%14s ' % header)

        btm_str = header_str + '\n'

        for left in self.table_left:
            btm_str += ('%14s ' % str(left))
            for header in self.table_header:
                btm_str += ('%14s ' % str((self.TM[(str(left), str(header))]['flows'],
                                          self.TM[(str(left), str(header))]['packets'],
                                          self.TM[(str(left), str(header))]['bytes'])))
            btm_str += '\n'

        btm_str = btm_str[:-1]

        return btm_str


def int_to_ipv4(addr):
    return "%d.%d.%d.%d" % \
           (addr >> 24 & 0xff, addr >> 16 & 0xff, addr >> 8 & 0xff, addr & 0xff)


def getNetFlowData(data):
    sdata = struct.unpack("!H", data[:2])
    version = sdata[0]

    if version == 1:
        print("NetFlow version %d:" % version)
        hformat = "!HHIII"
        # ! network (=big-endian), H - C unsigned short (2 bytes), I - C unsigned int (4 bytes)
        hlen = struct.calcsize(hformat)
        if len(data) < hlen:
            print("Truncated packet (header)")
            return 0, 0
        sheader = struct.unpack(hformat, data[:hlen])
        version = sheader[0]
        num_flows = sheader[1]
        # more header

        print(num_flows)
        fformat = "!IIIHHIIIIHHHBBBBBBI"
        # B - C unsigned char (1 byte)
        flen = struct.calcsize(fformat)

        if len(data) - hlen != num_flows * flen:
            print("Packet truncated (flows data)")
            return 0, 0

        flows = {}
        for n in range(num_flows):
            flow = {}
            offset = hlen + flen * n
            fdata = data[offset:offset + flen]
            sflow = struct.unpack(fformat, fdata)

            flow.update({'src_addr': int_to_ipv4(sflow[0])})
            flow.update({'dst_addr': int_to_ipv4(sflow[1])})
            flow.update({'next_hop': int_to_ipv4(sflow[2])})
            flow.update({'input_int_index': sflow[3]})
            flow.update({'output_int_index': sflow[4]})
            flow.update({'packets': sflow[5]})
            flow.update({'bytes': sflow[6]})
            flow.update({'start_time_of_flow': sflow[7]})
            flow.update({'end_time_of_flow': sflow[8]})
            flow.update({'source_port': sflow[9]})
            flow.update({'dst_port': sflow[10]})
            flow.update({'protocol': sflow[12]})
            flow.update({'tos': sflow[13]})
            flow.update({'tcp_flags': sflow[14]})
            # more flow
            flows.update({n: flow})

    elif version == 5:
        print("NetFlow version %d:" % version)
        hformat = "!HHIIIIBBH"
        # ! network (=big-endian), H - C unsigned short (2 bytes), I - C unsigned int (4 bytes)
        hlen = struct.calcsize(hformat)
        if len(data) < hlen:
            print("Truncated packet (header)")
            return 0, 0
        sheader = struct.unpack(hformat, data[:hlen])
        version = sheader[0]
        num_flows = sheader[1]
        # more header

        print(num_flows)
        fformat = "!IIIHHIIIIHHBBBBHHBBH"
        # B - C unsigned char (1 byte)
        flen = struct.calcsize(fformat)

        if len(data) - hlen != num_flows * flen:
            print("Packet truncated (flows data)")
            return 0, 0

        flows = {}
        for n in range(num_flows):
            flow = {}
            offset = hlen + flen * n
            fdata = data[offset:offset + flen]
            sflow = struct.unpack(fformat, fdata)

            flow.update({'src_addr': int_to_ipv4(sflow[0])})
            flow.update({'dst_addr': int_to_ipv4(sflow[1])})
            flow.update({'next_hop': int_to_ipv4(sflow[2])})
            flow.update({'input_int_index': sflow[3]})
            flow.update({'output_int_index': sflow[4]})
            flow.update({'packets': sflow[5]})
            flow.update({'bytes': sflow[6]})
            flow.update({'start_time_of_flow': sflow[7]})
            flow.update({'end_time_of_flow': sflow[8]})
            flow.update({'source_port': sflow[9]})
            flow.update({'dst_port': sflow[10]})
            flow.update({'tcp_flags': sflow[12]})
            flow.update({'ip_protocol': sflow[13]})
            flow.update({'TOS': sflow[14]})
            flow.update({'src_AS': sflow[15]})
            flow.update({'dst_AS': sflow[16]})
            flow.update({'src_netmask_len': sflow[17]})
            flow.update({'dst_netmask_len': sflow[18]})

            # more flow
            flows.update({n: flow})
    else:
        print("NetFlow version %d not supported!" % version)

    out = version, flows
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', nargs='?', type=int, help='listening UDP port', default=9996)
    parser.add_argument('-n', '--net', nargs='+', required=True, help='networks')
    parser.add_argument('-r', '--router', nargs='+', required=True, help='IP address(es) of NetFlow router(s)')
    args = parser.parse_args()

    nets = []
    for n in args.net:
        try:
            nn = IPNetwork(n)
            nets.append(nn)
        except:
            print('%s is not a network prefix' % n)

    print(nets)

    if len(nets) == 0:
        print("No valid network prefixes.")
        sys.exit()

    router = []
    for r in args.router:
        try:
            rr = IPAddress(r)
            router.append(rr)
        except:
            print('%s is not an IP address' % r)

    print(router)

    if len(router) == 0:
        print("No valid router IP address.")
        sys.exit()

    udp_port = args.port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.bind(('0.0.0.0', udp_port))

    print("listening on '0.0.0.0':%d" % udp_port)

    try:
        TM = Table(nets)

        while True:
            data, addr = sock.recvfrom(8192)  # buffer size is 1024 bytes
            version, flows = getNetFlowData(data)  # version=0 reports an error!

            if IPAddress(addr[0]) in router:
                num_flows = len(flows)

                print('Version: %d, from %s (%d)' % (version, addr[0], num_flows))

                for f in flows:
                    if IPAddress(flows[f]['src_addr']) in IPSet(nets):
                        source_addr = str(flows[f]['src_addr'])
                        source_ni = [IPAddress(source_addr) in net for net in nets].index(True)
                        source_network = str(nets[source_ni])
                    else:
                        source_network = 'other'

                    if IPAddress(flows[f]['dst_addr']) in IPSet(nets):
                        destination_addr = str(flows[f]['dst_addr'])
                        destination_ni = [IPAddress(destination_addr) in net for net in nets].index(True)
                        destination_network = str(nets[destination_ni])
                    else:
                        destination_network = 'other'

                    print("\nUpdated at: (%s, %s)\n" % (source_network, destination_network))

                    TM.update(source_network, destination_network, flows[f]['packets'], flows[f]['bytes'])

                    print("------------------------------------------------------------")
                    print(TM)
                    print("------------------------------------------------------------")
                    print("(flows, packets, bytes)\n\n")
            else:
                print('Version: %d, from %s' % (version, addr[0]))
                print('Other router NetFlow packet')

    except KeyboardInterrupt:
        sock.close()
        print("\nDone! Bye ;)")


if __name__ == "__main__":
    main()
