import socket
import random


class UDPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

    def listen(self):
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            data, addr = self.sock.recvfrom(1024)
            if random.randint(1, 5) != 1:
                request = data.decode('utf-8')
                response = request.upper()
                self.sock.sendto(response.encode('utf-8'), addr)
            else:
                print("Packet lost")

    def __del__(self):
        self.sock.close()


if __name__ == "__main__":
    server = UDPServer("localhost", 12345)
    server.listen()
