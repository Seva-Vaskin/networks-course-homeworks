import socket
import tkinter as tk


class DrawClient:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.root = tk.Tk()
        self.root.title("Client Canvas")
        self.canvas = tk.Canvas(self.root, bg='white', width=800, height=600)
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.paint)
        self.last_x, self.last_y = None, None
        self.root.mainloop()

    def paint(self, event):
        if self.last_x and self.last_y:
            x1, y1 = self.last_x, self.last_y
            x2, y2 = event.x, event.y
            self.canvas.create_line(x1, y1, x2, y2, fill='black')
            self.send_data(x1, y1, x2, y2)
        self.last_x, self.last_y = event.x, event.y

    def send_data(self, x1, y1, x2, y2):
        data = f"{x1},{y1},{x2},{y2}"
        self.client_socket.sendall(data.encode('utf-8'))


if __name__ == "__main__":
    DrawClient()
