from scapy.all import ARP, Ether, srp
import socket
import netifaces as ni
import tkinter as tk
from tkinter import ttk
import threading
from ipaddress import ip_network


def get_local_ip(interface):
    return ni.ifaddresses(interface)[ni.AF_INET][0]['addr']


def get_network_prefix(interface):
    return ni.ifaddresses(interface)[ni.AF_INET][0]['netmask']


def scan_network(ip_range):
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for sent, received in answered_list:
        try:
            hostname = socket.gethostbyaddr(received.psrc)[0]
        except socket.herror:
            hostname = "Unknown"
        devices.append({
            "ip": received.psrc,
            "mac": received.hwsrc,
            "hostname": hostname
        })
    return devices


class NetworkScannerGUI:
    def __init__(self, root, interface):
        self.root = root
        self.interface = interface
        self.setup_gui()

    def setup_gui(self):
        self.root.title("Network Scanner")
        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("IP", "MAC", "Hostname")
        self.tree.heading("#0", text="No.")
        self.tree.heading("IP", text="IP Address")
        self.tree.heading("MAC", text="MAC Address")
        self.tree.heading("Hostname", text="Hostname")

        self.tree.column("#0", width=50)
        self.tree.column("IP", width=150)
        self.tree.column("MAC", width=150)
        self.tree.column("Hostname", width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)

        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Start Scan", command=self.start_scan)
        self.start_button.pack(pady=10)

    def start_scan(self):
        self.start_button.config(state=tk.DISABLED)
        threading.Thread(target=self.scan_network, daemon=True).start()

    def scan_network(self):
        local_ip = get_local_ip(self.interface)
        netmask = get_network_prefix(self.interface)
        network = ip_network(f"{local_ip}/{netmask}", strict=False)
        ip_list = list(network.hosts())

        self.progress["maximum"] = len(ip_list)
        self.progress["value"] = 0

        total = 0
        for index, ip in enumerate(ip_list):
            self.progress["value"] = index + 1
            self.root.update_idletasks()
            devices = scan_network(str(ip))

            for device in devices:
                total += 1
                self.tree.insert("", "end", text=str(total),
                                 values=(device["ip"], device["mac"], device["hostname"]))

        self.start_button.config(state=tk.NORMAL)


def main(interface):
    root = tk.Tk()
    app = NetworkScannerGUI(root, interface)
    root.mainloop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("interface", type=str)
    args = parser.parse_args()

    main(args.interface)
