import signal
import socket
from pathlib import Path
import argparse
import threading


def extract_filename_from_request(request: str) -> Path:
    headers = request.split('\r\n')
    first_line = headers[0].split(' ')
    filename = first_line[1]
    return Path('.' + filename)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port to run the server on')
    parser.add_argument('--concurrent', default=False, action='store_true',
                        help='set this flag if concurrent mode should be used')
    return parser.parse_args()


class Socket:

    def __init__(self, server_name, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((server_name, port))
        self.server_socket.listen(1)
        self.server_socket.settimeout(1)

    def __del__(self):
        self.server_socket.close()

    def accept(self):
        return self.server_socket.accept()


running = True


def signal_handler(signum, frame):
    global running
    print('Signal received, shutting down...')
    running = False


def handle_client(connection_socket):
    request = connection_socket.recv(1024).decode('utf-8')
    filepath = extract_filename_from_request(request)
    print(f"Received filepath: {filepath.absolute()}")

    if filepath.is_file():
        header = 'HTTP/1.0 200 OK\r\n\r\n'
        with filepath.open('rb') as f:
            response = header.encode('utf-8') + f.read()
        print("File found")
    else:
        response = f'HTTP/1.0 404 NOT FOUND\r\n\r\n file {filepath} not found'.encode('utf-8')
        print(f"File {filepath} not found")

    connection_socket.sendall(response)
    connection_socket.close()


def main(port: int, concurrent: bool):
    print(f"File server is started. Port: {port}; Working dir: {Path().cwd()}")

    server_socket = Socket('localhost', port)

    while running:
        try:
            connection_socket, client_address = server_socket.accept()
        except TimeoutError:
            continue
        if concurrent:
            client_thread = threading.Thread(target=handle_client, args=(connection_socket,))
            client_thread.start()
        else:
            handle_client(connection_socket)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    arguments = parse_arguments()
    main(arguments.port, arguments.concurrent)
