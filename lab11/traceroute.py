import socket
import struct
import time
import argparse

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
ICMP_CODE = socket.getprotobyname('icmp')


def calculate_checksum(source_string):
    sm = 0
    max_count = (len(source_string) // 2) * 2
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


def create_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    data = struct.pack('d', time.time())
    checksum = calculate_checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, checksum, id, 1)
    return header + data


def trace_route(destination, max_hops, timeout, packet_count):
    try:
        dest_ip = socket.gethostbyname(destination)
    except socket.gaierror:
        print(f"Cannot resolve {destination}: Unknown host")
        return

    print(f"Tracing route to {destination} ({dest_ip}), {max_hops} hops max")

    packet_id = 0
    dest_found = False
    for ttl in range(1, max_hops + 1):
        if dest_found:
            break
        times = []
        reached_addr = [""]
        hostname = None
        for attempt in range(packet_count):
            icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, ICMP_CODE)
            icmp_socket.settimeout(timeout)
            icmp_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

            packet_id = (packet_id + 1) % 65535
            packet = create_packet(packet_id)

            send_time = time.time()
            icmp_socket.sendto(packet, (dest_ip, 1))

            try:
                rec_packet, addr = icmp_socket.recvfrom(1024)
                rec_time = time.time()
                elapsed_time = (rec_time - send_time) * 1000
                times.append(elapsed_time)
                reached_addr = addr
                try:
                    hostname = socket.gethostbyaddr(addr[0])[0]
                except:
                    hostname = None
                icmp_header = rec_packet[20:28]
                type, code, checksum, packet_id, sequence = struct.unpack('bbHHh', icmp_header)

                if type == ICMP_TIME_EXCEEDED:
                    pass
                elif type == ICMP_ECHO_REPLY:
                    dest_found = True
                else:
                    print(f"{ttl}\t{addr[0]}\tUnexpected ICMP type: {type}")

            except socket.timeout:
                times.append(None)

            finally:
                icmp_socket.close()

        if hostname is None:
            print(f"{ttl}\t{reached_addr[0]}\t", end='')
        else:
            print(f"{ttl}\t{reached_addr[0]} ({hostname})\t", end='')

        for t in times:
            if t is None:
                print("*\t", end='')
            else:
                print(f"{t:.2f} ms\t", end='')
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace the route to a network host using ICMP.")
    parser.add_argument("destination", help="The destination host to trace the route to.")
    parser.add_argument("--max-hops", type=int, default=30, help="Maximum number of hops (TTL).")
    parser.add_argument("--timeout", type=int, default=2, help="Timeout in seconds for each request.")
    parser.add_argument("--count", type=int, default=3, help="Number of packets to send per hop.")
    args = parser.parse_args()

    trace_route(args.destination, args.max_hops, args.timeout, args.count)
