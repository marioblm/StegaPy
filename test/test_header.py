import unittest
from src import header

FILETYPE_BYTES = 3
CONTENT_LENGTH_BITS = 24
BITS_PER_PIXEL = 2


class HeaderTest(unittest.TestCase):
    def setUp(self):
        self.h_u = header.HeaderUtils.instance(CONTENT_LENGTH_BITS, FILETYPE_BYTES, BITS_PER_PIXEL)

    def test_unsupported_filesize(self):
        with self.assertRaises(OverflowError):
            self.h_u.encode_header(self.h_u.max_filesize + 1, "", 1, False, False)

    def test_too_many_bits_per_pixel(self):
        with self.assertRaises(OverflowError):
            self.h_u.encode_header(self.h_u.max_filesize, "", self.h_u.max_bits_per_pixel + 1, True, True)

    def test_too_few_bits_per_channel(self):
        with self.assertRaises(OverflowError):
            self.h_u.encode_header(self.h_u.max_filesize, "", 0, True, True)

    def test_too_long_filetype(self):
        with self.assertRaises(OverflowError):
            self.h_u.encode_header(self.h_u.max_filesize, "ABCD", self.h_u.max_bits_per_pixel, True, True)

    def test_empty_file(self):
        headerBits = self.h_u.encode_header(0, "", 1, False, False)
        self.assertEqual(headerBits, '000000000000000000000000'+'000000000000000000000000'+'0000')

    def test_maximum_filesize(self):
        headerBits = self.h_u.encode_header(self.h_u.max_filesize, "", 1, False, False)
        self.assertEqual(headerBits, '111111111111111111111111'+'000000000000000000000000'+'0000')

    def test_encryption(self):
        headerBits = self.h_u.encode_header(self.h_u.max_filesize, "", 1, False, True)
        self.assertEqual(headerBits, '111111111111111111111111'+'000000000000000000000000'+'0001')

    def test_allchannels(self):
        headerBits = self.h_u.encode_header(self.h_u.max_filesize, "", 1, True, True)
        self.assertEqual(headerBits, '111111111111111111111111'+'000000000000000000000000'+'0011')

    def test_maximal_bits(self):
        headerBits = self.h_u.encode_header(self.h_u.max_filesize, "", self.h_u.max_bits_per_pixel, True, True)
        self.assertEqual(headerBits, '111111111111111111111111'+'000000000000000000000000'+'1111')

    def test_filetype(self):
        headerBits = self.h_u.encode_header(self.h_u.max_filesize, "AAA", self.h_u.max_bits_per_pixel, True, True)
        self.assertEqual(headerBits, '111111111111111111111111'+'01000001'+'01000001'+'01000001'+'1111')

    def test_filetype2(self):
        headerBits = self.h_u.encode_header(self.h_u.max_filesize, "~~~", self.h_u.max_bits_per_pixel, True, True)
        self.assertEqual(headerBits, '111111111111111111111111'+'01111110'+'01111110'+'01111110'+'1111')


class HeaderTestDecode(unittest.TestCase):
    def setUp(self):
        self.h_u = header.HeaderUtils.instance(CONTENT_LENGTH_BITS, FILETYPE_BYTES, BITS_PER_PIXEL)

    def test_unsupported_header(self):
        with self.assertRaises(ValueError):
            self.h_u.decode_header((self.h_u.header_length+1) * "0")

    def test_invalid_characters(self):
        with self.assertRaises(ValueError):
            self.h_u.decode_header(self.h_u.header_length * " ")

    def test_empty_file(self):
        header_data = list(self.h_u.decode_header('000000000000000000000000'+'000000000000000000000000'+'0000'))
        self.assertEqual(header_data, [0, "", 1, False, False])

    def test_maximum_filesize(self):
        header_data = list(self.h_u.decode_header('111111111111111111111111'+'000000000000000000000000'+'0000'))
        self.assertEqual(header_data, [self.h_u.max_filesize, "", 1, False, False])

    def test_encryption(self):
        header_data = list(self.h_u.decode_header('111111111111111111111111'+'000000000000000000000000'+'0001'))
        self.assertEqual(header_data, [self.h_u.max_filesize, "", 1, False, True])

    def test_allchannels(self):
        header_data = list(self.h_u.decode_header('111111111111111111111111'+'000000000000000000000000'+'0011'))
        self.assertEqual(header_data, [self.h_u.max_filesize, "", 1, True, True])

    def test_maximal_bits(self):
        header_data = list(self.h_u.decode_header('111111111111111111111111'+'000000000000000000000000'+'1111'))
        self.assertEqual(header_data, [self.h_u.max_filesize, "", self.h_u.max_bits_per_pixel, True, True])

    def test_filetype(self):
        header_data = list(self.h_u.decode_header('111111111111111111111111'+'01000001'+'01000001'+'01000001'+'1111'))
        self.assertEqual(header_data, [self.h_u.max_filesize, "AAA", self.h_u.max_bits_per_pixel, True, True])

    def test_filetype2(self):
        header_data = list(self.h_u.decode_header('111111111111111111111111'+'01111110'+'01111110'+'01111110'+'1111'))
        self.assertEqual(header_data, [self.h_u.max_filesize, "~~~", self.h_u.max_bits_per_pixel, True, True])
