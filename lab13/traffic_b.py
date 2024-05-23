from collections import defaultdict
from scapy.all import sniff, IP, TCP, UDP
import argparse
import netifaces as ni

incoming_traffic = defaultdict(int)
outgoing_traffic = defaultdict(int)
local_ip = None


def packet_callback(packet):
    global incoming_traffic, outgoing_traffic
    if packet.haslayer(IP):
        if packet[IP].dst == local_ip:
            if packet.haslayer(TCP):
                incoming_traffic[packet[TCP].dport] += len(packet)
            elif packet.haslayer(UDP):
                incoming_traffic[packet[UDP].dport] += len(packet)
            else:
                incoming_traffic[0] += len(packet)
        elif packet[IP].src == local_ip:
            if packet.haslayer(TCP):
                outgoing_traffic[packet[TCP].sport] += len(packet)
            elif packet.haslayer(UDP):
                outgoing_traffic[packet[UDP].sport] += len(packet)
            else:
                outgoing_traffic[0] += len(packet)


def get_local_ip(interface):
    return ni.ifaddresses(interface)[ni.AF_INET][0]['addr']


def main():
    global local_ip
    parser = argparse.ArgumentParser()
    parser.add_argument("interface", type=str)
    args = parser.parse_args()
    interface = args.interface
    local_ip = get_local_ip(interface)
    sniff(iface=interface, prn=packet_callback, store=0)

    print()
    print("Incoming traffic:")
    for port, traffic in incoming_traffic.items():
        print(f"Port {port}: {traffic} bytes")

    print("Outgoing traffic:")
    for port, traffic in outgoing_traffic.items():
        print(f"Port {port}: {traffic} bytes")


if __name__ == "__main__":
    main()
