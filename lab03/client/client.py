import socket
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('server_host', type=str, help='Hostname or IP address of the server')
    parser.add_argument('server_port', type=int, help='Port number of the server')
    parser.add_argument('filename', type=str, help='Name of the file to fetch')
    return parser.parse_args()


def connect_to_server(host, port, request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(request.encode())
        response = client_socket.recv(4096)
    return response


def main():
    args = parse_arguments()
    request = f"GET {args.filename} HTTP/1.0\r\n\r\n"
    response = connect_to_server(args.server_host, args.server_port, request)
    print(response.decode('utf-8'))


if __name__ == '__main__':
    main()
