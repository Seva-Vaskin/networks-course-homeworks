import argparse
import socket
import struct
import time
import select


class Ping:
    def __init__(self, target_host, count=10):
        self.target_host = target_host
        self.count = count
        self.packet_size = 64
        self.timeout = 1
        self.id = 0xABCD  # ICMP

    @staticmethod
    def checksum(source_string):
        sm = 0
        max_count = (len(source_string) / 2) * 2
        count = 0
        while count < max_count:
            val = source_string[count + 1] * 256 + source_string[count]
            sm = sm + val
            sm = sm & 0xffffffff
            count = count + 2
        if max_count < len(source_string):
            sm = sm + source_string[len(source_string) - 1]
            sm = sm & 0xffffffff
        sm = (sm >> 16) + (sm & 0xffff)
        sm = sm + (sm >> 16)
        answer = ~sm
        answer = answer & 0xffff
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def create_packet(self, icmp_seq):
        header = struct.pack("bbHHh", 8, 0, 0, self.id, icmp_seq)
        data = (192 - struct.calcsize("d")) * "Q"
        data = struct.pack("d", time.time()) + data.encode()
        my_checksum = self.checksum(header + data)
        header = struct.pack("bbHHh", 8, 0, socket.htons(my_checksum), self.id, icmp_seq)
        return header + data

    def ping_once(self, icmp_seq):
        icmp = socket.getprotobyname("icmp")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error as e:
            print("Ошибка создания сокета:", e)
            return
        packet = self.create_packet(icmp_seq)
        while packet:
            sent = sock.sendto(packet, (self.target_host, 1))
            packet = packet[sent:]
        delay = self.receive_ping(sock)
        sock.close()
        return delay

    def receive_ping(self, sock):
        time_left = self.timeout
        while True:
            start_select = time.time()
            what_ready = select.select([sock], [], [], time_left)
            how_long_in_select = (time.time() - start_select)
            if not what_ready[0]:  # Timeout
                return

            time_received = time.time()
            rec_packet, addr = sock.recvfrom(1024)
            icmp_header = rec_packet[20:28]
            tp, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)
            if packet_id == self.id:
                if tp == 0 and code == 0:
                    bytes_in_double = struct.calcsize("d")
                    time_sent = struct.unpack("d", rec_packet[28:28 + bytes_in_double])[0]
                    return time_received - time_sent
                elif tp == 3 and code == 0:
                    return "Destination network unreachable"
                elif tp == 3 and code == 1:
                    return "Destination host unreachable"
                else:
                    return f"Error type {tp} code {code}"

            time_left = time_left - how_long_in_select
            if time_left <= 0:
                return

    def run(self):
        print(f"PING {self.target_host} {self.packet_size} bytes of data:")
        delays = []
        for i in range(self.count):
            result = self.ping_once(i)
            if result is None:  # Timeout
                print("Request timed out.")
            elif isinstance(result, float):  # Delay
                delays.append(result)
                min_delay = min(delays)
                max_delay = max(delays)
                avg_delay = sum(delays) / len(delays)
                lost_packets = i + 1 - len(delays)
                loss_percentage = (lost_packets / (i + 1)) * 100
                print(f"Reply from {self.target_host}: icmp_seq={i} time={result * 1000:.2f}ms "
                      f"min={min_delay * 1000:.2f}ms, max={max_delay * 1000:.2f}ms, avg={avg_delay * 1000:.2f}ms "
                      f"succ={100 - loss_percentage:.0f}%")
            else:  # Error
                print(f"From {self.target_host}: {result} (icmp_seq={i})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str)
    args = parser.parse_args()

    pinger = Ping(args.ip)
    pinger.run()
