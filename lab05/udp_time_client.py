import socket

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.bind(("", 8888))

        while True:
            data, _ = client_socket.recvfrom(4096)
            print(f"Received time: {data.decode('utf-8')}")
