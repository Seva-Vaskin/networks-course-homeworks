import unittest


def uint16_add(a, b):
    mask = 0xFFFF
    assert 0 <= a <= mask
    assert 0 <= b <= mask
    sum = (a + b) & mask
    carry = (a + b) >> mask
    res = (sum + carry) & mask
    assert 0 <= res <= mask
    return res


def uint16_neg(a):
    mask = 0xFFFF
    assert 0 <= a <= mask
    res = (~a) & 0xFFFF
    assert res + a == mask
    assert 0 <= res <= mask
    return res


def calculate_checksum(data):
    sum = 0
    for i in range(0, len(data), 2):
        word = int.from_bytes(data[i:i + 2], byteorder='big', signed=False)
        sum = uint16_add(sum, word)

    return uint16_neg(sum)


def verify_checksum(data, received_checksum):
    sum = received_checksum
    for i in range(0, len(data), 2):
        word = int.from_bytes(data[i:i + 2], byteorder='big', signed=False)
        sum = uint16_add(sum, word)
    return sum == 0xFFFF


class TestChecksumFunctions(unittest.TestCase):

    def test_verify_checksum_correct(self):
        data_bytes = b'\x01\x02\x03\x04'
        checksum = calculate_checksum(data_bytes)
        self.assertTrue(verify_checksum(data_bytes, checksum))

    def test_verify_checksum_incorrect(self):
        data_bytes = b'\x01\x02\x03\x05'
        checksum = calculate_checksum(b'\x01\x02\x03\x04')
        self.assertFalse(verify_checksum(data_bytes, checksum))

    def test_verify_checksum_single_byte(self):
        data_bytes = b'\x01'
        checksum = calculate_checksum(data_bytes)
        self.assertTrue(verify_checksum(data_bytes, checksum))

    def test_verify_checksum_empty_data(self):
        data_bytes = b''
        checksum = calculate_checksum(data_bytes)
        self.assertTrue(verify_checksum(data_bytes, checksum))


if __name__ == '__main__':
    unittest.main()
