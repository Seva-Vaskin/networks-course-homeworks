import socket
import threading
import tkinter as tk


class DrawServer:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f'Server started and listening on {self.host}:{self.port}')
        self.conn, self.addr = self.server_socket.accept()
        print(f'Connected by {self.addr}')
        self.root = tk.Tk()
        self.root.title("Server Canvas")
        self.canvas = tk.Canvas(self.root, bg='white', width=800, height=600)
        self.canvas.pack()
        self.run()

    def run(self):
        threading.Thread(target=self.receive_data).start()
        self.root.mainloop()

    def receive_data(self):
        while True:
            data = self.conn.recv(1024).decode('utf-8')
            if not data:
                break
            coords = data.split(',')
            x1, y1, x2, y2 = map(float, coords)
            self.canvas.create_line(x1, y1, x2, y2, fill='black')


if __name__ == "__main__":
    DrawServer()
