import socket


class EchoServer:
    def __init__(self, host='::1', port=8888):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f'Server started and listening on {self.host}:{self.port}')

    def start(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f'Connected by {addr}')
            self.handle_client(conn)

    def handle_client(self, conn):
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                response = data.decode('utf-8').upper().encode('utf-8')
                conn.sendall(response)


if __name__ == "__main__":
    server = EchoServer()
    server.start()
