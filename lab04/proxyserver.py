import copy
import signal
import socket
import sys
import time
from pathlib import Path
import argparse
import threading
import logging

import requests


def log(msg, level=logging.INFO):
    print(msg)
    logging.log(level=level, msg=msg)


class ProxyClientHandler:
    def __init__(self, client_connection, client_address, semaphore, blacklist):
        self.client_connection = client_connection
        self.client_address = client_address
        self.semaphore = semaphore
        self.blacklist = blacklist
        log(f"Client connection with {self.client_address} started")

    @staticmethod
    def forward_traffic(source, dest):
        while True:
            data = source.recv(4096)
            dest.sendall(data)
            if len(data) < 4096:
                break

    def get_request(self):
        request = []
        while True:
            data = self.client_connection.recv(4096)
            request.extend(data)
            if len(data) < 4096:
                break
        return bytes(request).decode('utf-8')

    @staticmethod
    def bad_request_response():
        return 'HTTP/1.1 400 Bad Request\r\n\r\n'.encode('utf-8')

    @staticmethod
    def not_found_response():
        return 'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n'.encode('utf-8')

    @staticmethod
    def ok_response(content):
        return f'HTTP/1.1 200 OK\r\nContent-Length: {len(content)}\r\n\r\n{content}'.encode('utf-8')

    def handle(self):
        with self.semaphore:
            try:
                client_request = self.get_request()
                method, url, http_version = client_request.split(' ', 4)[:3]
                print(f"Got request: {method} {url} {http_version}")
                assert url[0] == '/'
                url = url[1:]

                if url in self.blacklist:
                    self.client_connection.sendall(self.ok_response(f"{url} is in the blacklist"))
                    log(f"{url} is in blacklist => refuse")
                    return

                referer = [i for i in client_request.split('\n') if 'Referer:' in i]
                if referer:
                    server_name = copy.copy(referer[0])
                    if (proto_del_pos := server_name.find("://")) != -1:
                        server_name = server_name[proto_del_pos + 3:]
                    server_name = server_name.split('/', 1)[1]
                    server_name = server_name.rstrip('/\r\n')
                    url = "{}/{}".format(server_name, url)
                if not url.startswith("http://") and not url.startswith("https://"):
                    url = "https://" + url

                print(f"Requesting url: {url}")

                if method == 'GET':
                    response = requests.get(url)
                    log(f"Got answer with code 200 for {url}")
                elif method == 'POST':
                    data = client_request.split('\r\n\r\n', 1)[1]
                    response = requests.post(url, data=data)
                else:
                    self.client_connection.sendall(self.bad_request_response())
                    log(f"Bad request 400 for {url}")
                    return

                if response.status_code == 404:
                    log(f"Not found {url}")
                    self.client_connection.sendall(self.not_found_response())
                else:
                    log(f"Got response from {url} with code {response.status_code}")
                    self.client_connection.sendall(self.ok_response(response.content.decode('utf-8')))

            except Exception as e:
                self.client_connection.sendall(self.bad_request_response())

    def __del__(self):
        self.client_connection.close()
        log(f"Client connection with {self.client_address} closed")


class ProxyServer:
    def __init__(self, host, port, concurrency_level):
        self.port = port
        self.semaphore = threading.Semaphore(concurrency_level)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1)
        self.running = True
        with (Path(__file__).parent / "blacklist.txt").open('r') as f:
            self.blacklist = set(f.read().split('\n'))

    def run(self):
        log(f"Proxy server started on port {self.port}")

        while self.running:
            try:
                client_connection, client_address = self.server_socket.accept()
                client_handler = ProxyClientHandler(client_connection, client_address, self.semaphore, self.blacklist)
                client_thread = threading.Thread(target=client_handler.handle)
                client_thread.start()
            except socket.timeout:
                continue

        log("Proxy server shut down")

    def stop(self):
        self.running = False


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=8888, type=int, help='Port to run the proxy server on')
    parser.add_argument('--concurrency_level', default=10, type=int, help='Maximum number of concurrent threads')
    return parser.parse_args()


def signal_handler(signum, frame, server):
    print('Signal received, shutting down...')
    server.stop()


def main():
    args = parse_arguments()
    logging.basicConfig(filename='proxy.log', level=logging.INFO)
    proxy_server = ProxyServer('localhost', args.port, args.concurrency_level)
    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, proxy_server))
    signal.signal(signal.SIGTERM, lambda signum, frame: signal_handler(signum, frame, proxy_server))
    proxy_server.run()


if __name__ == '__main__':
    main()
