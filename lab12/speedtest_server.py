import socket
import tkinter as tk
import threading
import time


class SpeedtestServer:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP/UDP Server")

        self.protocol = tk.StringVar(value="TCP")

        tk.Label(root, text="Enter IP:").grid(row=0, column=0)
        self.ip_entry = tk.Entry(root)
        self.ip_entry.grid(row=0, column=1)

        tk.Label(root, text="Enter Port:").grid(row=1, column=0)
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=1, column=1)

        tk.Label(root, text="Protocol:").grid(row=2, column=0)
        tk.Radiobutton(root, text="TCP", variable=self.protocol, value="TCP").grid(row=2, column=1)
        tk.Radiobutton(root, text="UDP", variable=self.protocol, value="UDP").grid(row=2, column=2)

        self.start_button = tk.Button(root, text="Start", command=self.start_server)
        self.start_button.grid(row=3, column=0, columnspan=2)

        tk.Label(root, text="Status:").grid(row=4, column=0)
        self.status_label = tk.Label(root, text="")
        self.status_label.grid(row=4, column=1)

        tk.Label(root, text="Received Packets:").grid(row=5, column=0)
        self.received_packets_label = tk.Label(root, text="0")
        self.received_packets_label.grid(row=5, column=1)

        tk.Label(root, text="Lost Packets:").grid(row=6, column=0)
        self.lost_packets_label = tk.Label(root, text="0")
        self.lost_packets_label.grid(row=6, column=1)

    def start_server(self):
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        protocol = self.protocol.get()

        threading.Thread(target=self._start_server, args=(ip, port, protocol)).start()

    def _start_server(self, ip, port, protocol):
        if protocol == "TCP":
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((ip, port))
            server_socket.listen(1)
            conn, addr = server_socket.accept()
            self._receive_data_tcp(conn)
        else:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind((ip, port))
            self._receive_data_udp(server_socket)

    def _receive_data_tcp(self, conn):
        total_data = 0
        packet_count = 0
        start_time = time.time()
        while True:
            data = conn.recv(1024)
            if not data:
                break
            total_data += len(data)
            packet_count += 1
            self.received_packets_label.config(text=f"{packet_count}")
            self._update_speed(total_data, start_time)
        conn.close()

    def _receive_data_udp(self, server_socket):
        total_data = 0
        packet_count = 0
        start_time = time.time()
        while True:
            data, addr = server_socket.recvfrom(1024)
            if not data:
                break
            total_data += len(data)
            packet_count += 1
            self.received_packets_label.config(text=f"{packet_count}")
            self._update_speed(total_data, start_time)

    def _update_speed(self, total_data, start_time):
        duration = time.time() - start_time
        if duration > 0:
            speed = f"{total_data / duration:.2f}"
        else:
            speed = "inf"
        self.status_label.config(text=f"{speed} B/s")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedtestServer(root)
    root.mainloop()
