import socket
import time
from datetime import datetime

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # server_socket.settimeout(0.2)

        while True:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            server_socket.sendto(now.encode('utf-8'), ('<broadcast>', 8888))
            print(f"Sent time: {now}")
            time.sleep(1)
