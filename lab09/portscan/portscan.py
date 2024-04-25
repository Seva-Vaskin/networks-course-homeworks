import socket
import sys


def check_ports(ip, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"Port {port} is taken", file=sys.stderr)
        else:
            open_ports.append(port)
        sock.close()
    return open_ports


if __name__ == "__main__":
    ip = sys.argv[1]
    begin = int(sys.argv[2])
    end = int(sys.argv[3])

    free_ports = check_ports(ip, begin, end)
    print(*free_ports, sep='\n')
