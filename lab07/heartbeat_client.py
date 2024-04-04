import datetime
import random
import socket
import time


class UDPClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_heartbeat(self, sequence_number):
        timestamp = time.time()
        message = f"{sequence_number} {timestamp:.10f}"
        self.sock.sendto(message.encode('utf-8'), (self.server_host, self.server_port))

    def __del__(self):
        self.sock.close()


if __name__ == "__main__":
    client = UDPClient("localhost", 12345)
    sequence_number = 0
    while True:
        sequence_number += 1
        if random.randint(1, 3) == 1:
            print("Emulated miss")
        else:
            client.send_heartbeat(sequence_number)
            print(f"Heartbeat {sequence_number} sent")
        time.sleep(1)
