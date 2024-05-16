import socket
import tkinter as tk
import time
import random
import threading


class SpeedtestClient:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP/UDP Client")

        self.protocol = tk.StringVar(value="TCP")

        tk.Label(root, text="Enter Server IP:").grid(row=0, column=0)
        self.server_ip_entry = tk.Entry(root)
        self.server_ip_entry.grid(row=0, column=1)

        tk.Label(root, text="Enter Port:").grid(row=1, column=0)
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=1, column=1)

        tk.Label(root, text="Number of Packets:").grid(row=2, column=0)
        self.packet_entry = tk.Entry(root)
        self.packet_entry.grid(row=2, column=1)

        tk.Label(root, text="Protocol:").grid(row=3, column=0)
        tk.Radiobutton(root, text="TCP", variable=self.protocol, value="TCP").grid(row=3, column=1)
        tk.Radiobutton(root, text="UDP", variable=self.protocol, value="UDP").grid(row=3, column=2)

        self.send_button = tk.Button(root, text="Send", command=self.send_packets)
        self.send_button.grid(row=4, column=0, columnspan=2)

        tk.Label(root, text="Status:").grid(row=5, column=0)
        self.status_label = tk.Label(root, text="")
        self.status_label.grid(row=5, column=1)

    def send_packets(self):
        server_ip = self.server_ip_entry.get()
        port = int(self.port_entry.get())
        num_packets = int(self.packet_entry.get())
        protocol = self.protocol.get()

        threading.Thread(target=self._send_packets, args=(server_ip, port, num_packets, protocol)).start()

    def _send_packets(self, server_ip, port, num_packets, protocol):
        if protocol == "TCP":
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, port))
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        start_time = time.time()
        lost_packets = 0
        for i in range(num_packets):
            data = random._urandom(1024)
            try:
                if protocol == "TCP":
                    client_socket.send(data)
                else:
                    client_socket.sendto(data, (server_ip, port))
            except:
                lost_packets += 1
            time.sleep(0.01)

        end_time = time.time()
        duration = end_time - start_time
        client_socket.close()
        self.status_label.config(
            text=f"Sent {num_packets - lost_packets}/{num_packets} packets in {duration:.2f} seconds")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedtestClient(root)
    root.mainloop()
