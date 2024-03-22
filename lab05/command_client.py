import socket


class CommandClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_command(self, command):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(command.encode('utf-8'))
            data = s.recv(1024)
            print(f"{data.decode('utf-8')}")


if __name__ == "__main__":
    client = CommandClient('localhost', 8888)
    while command := input("Enter command to execute: "):
        client.send_command(command)
