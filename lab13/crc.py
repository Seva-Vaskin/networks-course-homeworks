import argparse


def crc32(bytes_data):
    crc_table = [0] * 256
    for i in range(256):
        crc = i
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc >>= 1
        crc_table[i] = crc

    crc = 0xFFFFFFFF
    for byte in bytes_data:
        crc = crc_table[(crc ^ byte) & 0xFF] ^ (crc >> 8)

    return crc ^ 0xFFFFFFFF


class Packet:
    def __init__(self, data: bytes):
        self.data = data
        self.crc = self.compute_crc()

    def compute_crc(self):
        return crc32(self.data)

    def encode_packet(self):
        return self.data + self.crc.to_bytes(4, byteorder='big')

    @staticmethod
    def verify_crc(encoded_packet: bytes):
        data, received_crc = encoded_packet[:-4], int.from_bytes(encoded_packet[-4:], byteorder='big')
        computed_crc = crc32(data)
        return computed_crc == received_crc


def make_error(encoded_packet: bytes, byte_index: int, bit_index: int):
    altered_packet = bytearray(encoded_packet)
    altered_packet[byte_index] ^= 1 << bit_index
    return bytes(altered_packet)


def main(input_text: str):
    packets = [Packet(input_text[i:i + 5].encode('utf-8')) for i in range(0, len(input_text), 5)]

    for i, packet in enumerate(packets):
        encoded_packet = packet.encode_packet()
        print(f"Packet {i + 1}:")
        print(f"\tData: {packet.data}")
        print(f"\tEncoded: {encoded_packet}")
        print(f"\tCRC: {packet.crc}")

        if i == 2:
            encoded_packet = make_error(encoded_packet, 5, 2)
            print(f"\tMade Error in Encoded: {encoded_packet}")
            broken = True
        else:
            broken = False

        if Packet.verify_crc(encoded_packet):
            print("\tCRC Check: Passed")
            assert not broken
        else:
            print("\tCRC Check: Failed")
            assert broken
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_text", type=str)
    args = parser.parse_args()
    main(args.input_text)
