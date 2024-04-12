from __future__ import annotations

import socket
import random
import struct
import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Any, BinaryIO

REPEATS = 200
TIMEOUT = 0.1
LOSS_RATE = 0.3


def addresses_eq(a1, a2):
    return socket.gethostbyname(a1[0]) != socket.gethostbyname(a2[0]) or a1[1] != a2[1]


class Packet:
    class Tags:
        ACK = 1
        SOF = 2
        EOF = 3
        DATA = 4
        ERROR = 5

        @staticmethod
        def valid_values():
            return range(1, 6)

    @dataclass
    class Header:
        identifier: int
        tag: int
        checksum: int

        @staticmethod
        def size() -> int:
            return 6

        def to_bytes(self) -> bytes:
            return struct.pack("!BBI", self.identifier, self.tag, self.checksum)

        @classmethod
        def from_bytes(cls, data: bytes) -> Packet.Header:
            identifier, tag, checksum = struct.unpack("!BBI", data)
            return cls(identifier, tag, checksum)

    @staticmethod
    def max_size() -> int:
        return 64

    @staticmethod
    def max_data_size() -> int:
        return Packet.max_size() - Packet.Header.size()

    @property
    def checksum(self) -> int:
        return hash(self.data) & 0xFFFF_FFFF

    def check_checksum(self):
        return self.header.checksum != self.checksum

    def __init__(self, identifier: int, tag: int, data: bytes = b""):
        if len(data) > self.max_data_size():
            raise ValueError(f"{self.__class__.__name__}: data is larger than max data size")
        if identifier not in (0, 1):
            raise ValueError(f"{self.__class__.__name__}: identifier should be 0 or 1")
        if tag not in Packet.Tags.valid_values():
            raise ValueError(f"{self.__class__.__name__}: unsupported tag")
        self.data = data
        self.header = Packet.Header(identifier, tag, self.checksum)

    def to_bytes(self) -> bytes:
        encoded = self.header.to_bytes() + self.data
        assert len(encoded) <= self.max_size()
        return encoded

    @classmethod
    def from_bytes(cls, data: bytes) -> Packet:
        if len(data) > cls.max_size():
            raise ValueError(f"{cls.__name__}: data length is larger than max data size")
        if len(data) < cls.Header.size():
            raise ValueError(f"{cls.__name__}: data length is less than header size")

        header = Packet.Header.from_bytes(data[:cls.Header.size()])
        data = data[cls.Header.size():]
        packet = Packet(header.identifier, header.tag, data)
        return packet


class BaseProtocol:
    def __init__(self, loss_chance=0.3, timeout=2):
        self.loss_chance = loss_chance
        self.timeout = timeout
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
        self.packet_id = 0

    def flip_packet_id(self):
        self.packet_id ^= 1
        print(f"Packet id flipped to {self.packet_id}")

    def check_packet(self, packet: Packet):
        return (packet.header.identifier == self.packet_id
                and packet.checksum == packet.header.checksum
                and packet.header.tag in Packet.Tags.valid_values())

    def send_packet(self, packet, address):
        if random.random() < self.loss_chance:
            print("Packet is lost")
            return
        self.socket.sendto(packet.to_bytes(), address)

    def safe_send_packet(self, packet_to_send: Packet, address: Any, repeats=REPEATS):
        for i in range(repeats):
            print(f"Try to send package {packet_to_send.header}. Attempt {i + 1}: {packet_to_send.data}")
            self.send_packet(packet_to_send, address)
            print(f"Try to receive ack")
            received = self.receive_packet()
            if received is None:
                print("Didn't receive any response")
                continue
            packet_received, address_received = received
            if addresses_eq(address_received, address):
                raise RuntimeError(f"Multiple connections are not implemented: {address_received} != {address}")
            if self.check_packet(packet_received) and packet_received.header.tag == Packet.Tags.ACK:
                print("Ack received => Successfully sent")
                self.flip_packet_id()
                return
            elif packet_received.header.identifier != self.packet_id:
                print("wrong expected_id")
                continue
            elif packet_received.header.tag == Packet.Tags.ERROR:
                print("Error message received => terminating")
                raise RuntimeError("Wrong protocol")
            else:
                self.send_packet(Packet(packet_to_send.header.identifier, Packet.Tags.ERROR), address)
                raise RuntimeError("Wrong protocol")
        raise ConnectionError(f"The {address} is not replying")

    def receive_packet(self) -> Optional[Tuple[Packet, Any]]:
        try:
            data, address = self.socket.recvfrom(Packet.max_size())
            return Packet.from_bytes(data), address
        except socket.timeout:
            print("Timeout")
            return None
        raise RuntimeError("Unreachable code executed")

    def safe_receive_packet(self, repeats=REPEATS) -> Tuple[Packet, Any]:
        for i in range(repeats):
            print(f"Try to receive packet with id {self.packet_id}. Attempt {i + 1}")
            received = self.receive_packet()
            if received is None:
                print("Failed to receive")
                continue
            packet, address = received
            print(f"Received packet {packet.header}")
            if self.check_packet(packet):
                print("Packet is correct")
                ack_packet = Packet(packet.header.identifier, Packet.Tags.ACK)
                self.send_packet(ack_packet, address)
                self.flip_packet_id()
                return packet, address
            elif packet.header.identifier != self.packet_id:
                ack_packet = Packet(packet.header.identifier, Packet.Tags.ACK)
                self.send_packet(ack_packet, address)
                print("Wrong identifier => Try one more time")
                continue
            else:
                print("Packet is incorrect")
                self.send_packet(Packet(self.packet_id, Packet.Tags.ERROR), address)
                raise RuntimeError("Wrong protocol")
        raise ConnectionError("Cannot receive packet")

    def send_file(self, filepath: Path, address: Any):
        def send_part(tag, data=b""):
            packet = Packet(self.packet_id, tag, data)
            self.safe_send_packet(packet, address)

        with open(filepath, "rb") as file:
            print("Sending SOF")
            send_part(Packet.Tags.SOF, filepath.name.encode('utf-8'))
            while data := file.read(Packet.max_data_size()):
                print(f"Sending data: {data}")
                send_part(Packet.Tags.DATA, data)
            print("Sending EOF")
            send_part(Packet.Tags.EOF, data)

    def receive_file(self, filepath: Path, from_address: Any, sof: bool):
        with open(filepath, "wb") as file:
            print("Start receiving file")
            while True:
                packet, address = self.safe_receive_packet()
                if addresses_eq(address, from_address):
                    raise RuntimeError("Multiple connections are not supported")
                if packet.header.tag == Packet.Tags.ERROR:
                    print("Error message received => terminating")
                    raise RuntimeError("Wrong protocol")
                elif packet.header.tag == Packet.Tags.SOF:
                    if sof:
                        self.send_packet(Packet(self.packet_id, Packet.Tags.ERROR), address)
                        raise RuntimeError("Protocol error: SOF already recieved")
                    sof = True
                elif packet.header.tag == Packet.Tags.DATA:
                    if not sof:
                        self.send_packet(Packet(self.packet_id, Packet.Tags.ERROR), address)
                        raise RuntimeError("Protocol error: expected SOF before DATA")
                    file.write(packet.data)
                elif packet.header.tag == Packet.Tags.EOF:
                    print("EOF found, file received")
                    break
                else:
                    raise ValueError("Received unsupported for file receiving tag")
            print("Finish receiving file")

    @staticmethod
    def check_filename(filename: str):
        pattern = r'^[!_.\da-zA-Z]+$'
        return bool(re.fullmatch(pattern, filename))


class Server(BaseProtocol):
    def __init__(self, port: int, save_dir: Path, loss_chance=LOSS_RATE, timeout=TIMEOUT):
        super().__init__(loss_chance, timeout)
        self.socket.bind(('localhost', port))
        self.save_dir = save_dir

    def handle_sof_packet(self, packet: Packet, address: Any):
        print("Start file transfer conversation")
        ack_packet = Packet(0, Packet.Tags.ACK)
        print(f"Send ack to {address}")
        self.send_packet(ack_packet, address)
        filename = packet.data.decode('utf-8')
        if not self.check_filename(filename):
            raise ValueError(f"Invalid filename {filename} => Skip")
        self.receive_file(self.save_dir / Path(filename), address, sof=True)
        print("Server: file received")
        print("Server: Sending file back")
        self.send_file(Path(filename), address)
        print("Server: file sent")

    def start(self):
        while True:
            received = self.receive_packet()
            if received is None:
                print("Wait for data...")
                continue
            try:
                packet, address = received
                print(f"Received {packet.header} as a beginning of the conversation: {packet.data}")
                if not self.check_packet(packet):
                    raise ValueError("Invalid packet received => Skip")
                if packet.header.tag == Packet.Tags.SOF:
                    self.handle_sof_packet(packet, address)
                    print("Data transmitted")
                    break
                else:
                    raise ValueError(
                        f"Unsupported packet {packet.header} for the beginning of conversation => Skip: {packet.data}")
            except RuntimeError as e:
                print(e)
                break
            except BaseException as e:
                print(e)
                continue


class Client(BaseProtocol):
    def __init__(self, server_address: Any, server_port: int, save_dir: Path, loss_chance=LOSS_RATE, timeout=TIMEOUT):
        super().__init__(loss_chance, timeout)
        self.server_address = (server_address, server_port)
        self.save_dir = save_dir

    def send(self, filepath: Path):
        print("client: start sending file")
        self.send_file(filepath, self.server_address)
        print("Client: file sent")
        print("Client: start receiving file back")
        self.receive_file(self.save_dir / filepath.name, self.server_address, sof=False)
        print("Client: file received back")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Mode of operation: server or client")
    parser.add_argument("save_dir", help="Directory to save files")
    parser.add_argument("--server_address", type=str)
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--filepath", type=str)

    args = parser.parse_args()
    Path(args.save_dir).mkdir(exist_ok=True, parents=True)
    if args.mode == "server":
        server = Server(args.port, Path(args.save_dir))
        server.start()
    elif args.mode == "client":
        assert args.port is not None
        assert args.server_address is not None
        assert args.filepath is not None
        client = Client(args.server_address, args.port, Path(args.save_dir))
        client.send(Path(args.filepath))
    else:
        assert False
