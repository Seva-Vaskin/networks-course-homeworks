import socket
import subprocess


class CommandServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start_server(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                print(f"Listening on {self.host}:{self.port}")

                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        try:
                            command = data.decode('utf-8')
                            print(f"Executing \"{command}\"")
                            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
                            output = result.stdout
                        except Exception as e:
                            print(f"Error occurred: {e}")
                            output = str(e).encode('utf-8')
                        conn.sendall(output)


if __name__ == "__main__":
    server = CommandServer('localhost', 8888)
    server.start_server()
