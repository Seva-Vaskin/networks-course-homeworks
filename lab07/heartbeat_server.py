import socket
import threading
import time
from collections import defaultdict


class UDPServer:
    def __init__(self, host, port, inactivity_timeout=10):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.clients = defaultdict(lambda: {'last_seq': 0, 'last_time': time.time()})
        self.inactivity_timeout = inactivity_timeout
        self.clients_lock = threading.Lock()
        self.active = True

    def handle_client(self, data, addr):
        seq, timestamp = data.decode('utf-8').split()
        seq = int(seq)
        timestamp = float(timestamp)
        now = time.time()
        delay = now - timestamp
        with self.clients_lock:
            client = self.clients[addr]

        expected_seq = client['last_seq'] + 1
        if seq > expected_seq:
            print(f"Packet loss detected from {addr}. Missing packets from {expected_seq} to {seq - 1}, packet {seq}, "
                  f"delay {delay:.3f} seconds")
        else:
            print(f"Ok from {addr}, packet {expected_seq}, delay {delay:.3f} seconds")
        client['last_seq'] = seq
        client['last_time'] = now

    def check_inactivity(self):
        while self.active:
            current_time = time.time()
            with self.clients_lock:
                inactive_clients = [addr for addr, client in self.clients.items() if
                                    current_time - client['last_time'] > self.inactivity_timeout]
            for addr in inactive_clients:
                print(f"Client {addr} is assumed stopped. No heartbeat received for {self.inactivity_timeout} seconds.")
                with self.clients_lock:
                    del self.clients[addr]
            time.sleep(1)

    def listen(self):
        print(f"Server is listening on {self.host}:{self.port}")
        threading.Thread(target=self.check_inactivity, daemon=True).start()
        while True:
            data, addr = self.sock.recvfrom(1024)
            threading.Thread(target=self.handle_client, args=(data, addr)).start()

    def __del__(self):
        self.active = False


if __name__ == "__main__":
    server = UDPServer("localhost", 12345)
    server.listen()
