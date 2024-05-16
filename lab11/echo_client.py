import socket


class EchoClient:
    def __init__(self, host='::1', port=8888):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_message(self, message):
        self.client_socket.sendall(message.encode('utf-8'))
        response = self.client_socket.recv(1024)
        return response.decode('utf-8')

    def close(self):
        self.client_socket.close()


if __name__ == "__main__":
    client = EchoClient()
    message = input("Enter a message to send to the server: ")
    response = client.send_message(message)
    print(f'Received from server: {response}')
    client.close()
