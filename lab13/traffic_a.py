from scapy.all import sniff
import argparse
import netifaces as ni

incoming_traffic = 0
outgoing_traffic = 0
local_ip = None


def packet_callback(packet):
    global incoming_traffic, outgoing_traffic
    if packet.haslayer("IP"):
        if packet["IP"].dst == local_ip:
            incoming_traffic += len(packet)
        elif packet["IP"].src == local_ip:
            outgoing_traffic += len(packet)


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
    print(f"Incoming traffic: {incoming_traffic} bytes")
    print(f"Outgoing traffic: {outgoing_traffic} bytes")


if __name__ == "__main__":
    main()
