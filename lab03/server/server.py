import signal
import socket
import time
from pathlib import Path
import argparse
import threading


class ClientHandler:
    def __init__(self, connection_socket, semaphore):
        self.connection_socket = connection_socket
        self.semaphore = semaphore

    @staticmethod
    def extract_filename_from_request(request: str) -> Path:
        headers = request.split('\r\n')
        first_line = headers[0].split(' ')
        filename = first_line[1]
        return Path('.' + filename)

    def handle(self):
        with self.semaphore:
            time.sleep(1)
            request = self.connection_socket.recv(1024).decode('utf-8')
            filepath = self.extract_filename_from_request(request)
            print(f"Received filepath: {filepath.absolute()}")

            if filepath.is_file():
                header = 'HTTP/1.0 200 OK\r\n\r\n'
                with filepath.open('rb') as f:
                    response = header.encode('utf-8') + f.read()
                print("File found")
            else:
                response = f'HTTP/1.0 404 NOT FOUND\r\n\r\n file {filepath} not found'.encode('utf-8')
                print(f"File {filepath} not found")

            self.connection_socket.sendall(response)
            self.connection_socket.close()


class Server:
    def __init__(self, host, port, concurrency_level):
        self.port = port
        self.semaphore = threading.Semaphore(concurrency_level)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1)
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        print(f"File server is started. Port: {self.port}; Working dir: {Path().cwd()}")

        while self.running:
            try:
                connection_socket, client_address = self.server_socket.accept()
            except TimeoutError:
                continue
            client_handler = ClientHandler(connection_socket, self.semaphore)
            client_thread = threading.Thread(target=client_handler.handle)
            client_thread.start()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port to run the server on')
    parser.add_argument('concurrency_level', type=int, help='Maximum number of concurrent threads')
    return parser.parse_args()


def signal_handler(signum, frame, server):
    print('Signal received, shutting down...')
    server.stop()


def main():
    arguments = parse_arguments()
    server = Server('localhost', arguments.port, arguments.concurrency_level)
    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, server))
    signal.signal(signal.SIGTERM, lambda signum, frame: signal_handler(signum, frame, server))
    server.run()


if __name__ == '__main__':
    main()
