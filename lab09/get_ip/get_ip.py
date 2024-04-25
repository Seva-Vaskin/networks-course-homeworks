import socket
import netifaces


def get_ip_and_netmask(interface):
    addrs = netifaces.ifaddresses(interface)
    ip_info = addrs[netifaces.AF_INET][0]
    ip_address = ip_info['addr']
    netmask = ip_info['netmask']
    return ip_address, netmask


def main():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        try:
            ip_address, netmask = get_ip_and_netmask(interface)
            print(f"Interface: {interface}")
            print(f"IP: {ip_address}")
            print(f"Mask: {netmask}\n")
        except KeyError:
            continue


if __name__ == "__main__":
    main()
