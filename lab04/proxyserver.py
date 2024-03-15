import signal
import socket
import threading
import argparse


class Server:
    def __init__(self, host, port, concurrency_level):
        self.port = port
        self.semaphore = threading.Semaphore(concurrency_level)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(50)  # Увеличиваем размер очереди ожидания
        self.server_socket.settimeout(1)
        self.running = True

    def stop(self):
        self.running = False
        self.server_socket.close()

    def run(self):
        print(f"Proxy server is started on port: {self.port}")

        while self.running:
            try:
                connection_socket, _ = self.server_socket.accept()
                client_handler = ClientHandler(connection_socket, self.semaphore)
                client_thread = threading.Thread(target=client_handler.handle)
                client_thread.start()
            except socket.timeout:
                continue

        print("Proxy server is shut down")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8888, help='Port to run the server on')
    parser.add_argument('--concurrency_level', type=int, default=10, help='Maximum number of concurrent connections')
    return parser.parse_args()


def signal_handler(signum, frame, server):
    print('Signal received, shutting down...')
    server.stop()


def main():
    args = parse_arguments()
    server = Server('localhost', args.port, args.concurrency_level)
    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, server))
    signal.signal(signal.SIGTERM, lambda signum, frame: signal_handler(signum, frame, server))
    server.run()


if __name__ == '__main__':
    main()
