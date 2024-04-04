import datetime
import socket


class UDPClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1)

    def send_echo_request(self, message):
        try:
            self.sock.sendto(message.encode('utf-8'), (self.server_host, self.server_port))
            received_message, _ = self.sock.recvfrom(1024)
            return received_message.decode('utf-8')
        except socket.timeout:
            return None

    def __del__(self):
        self.sock.close()


def show_stat(rtt_values, n):
    min_rtt = min(rtt_values)
    max_rtt = max(rtt_values)
    avg_rtt = sum(rtt_values) / len(rtt_values)
    print(
        f"\n{n} packets transmitted, {len(rtt_values)} packets received,"
        f" {((n - len(rtt_values)) / n) * 100:0.3f}% packet loss")
    print(f"rtt min/avg/max = {min_rtt:.3f}/{avg_rtt:.3f}/{max_rtt:.3f} ms\n")


if __name__ == "__main__":
    rtt_values = []
    client = UDPClient("localhost", 12345)
    N = 10
    for sequence_number in range(N):
        send_time = datetime.datetime.now()
        message = f"Ping {sequence_number + 1} {send_time}"
        received_message = client.send_echo_request(message)
        if received_message:
            rtt = (datetime.datetime.now() - send_time).total_seconds()
            print(f"Received: {received_message} RTT: {rtt:.5f} seconds")
            rtt_values.append(rtt * 1000)
            show_stat(rtt_values, sequence_number + 1)
        else:
            print("Request timed out\n")
