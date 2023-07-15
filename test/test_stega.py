import unittest
from src import steg
import os
import shutil

class StegaTest(unittest.TestCase):
    
    def setUp(self):
        self.temp_folder = "test_temp"
        self.medium = "./test/files/medium.png"
        self.encoded = os.path.join(self.temp_folder, "encoded")
        self.decoded = os.path.join(self.temp_folder, "decoded")
        self.key = b'00000000000000000000000000000000'
        os.mkdir(self.temp_folder)

    def test_unsupported_filesize(self):
        with self.assertRaises(OverflowError):
            steg.encode(medium_filename=self.medium, message_filename="./test/files/big.txt", hidden_filename=self.encoded)

    def test_unsupported_filetype(self):
        with self.assertRaises(OverflowError):
            steg.encode(medium_filename=self.medium, message_filename="./test/files/test.html", hidden_filename=self.encoded)

    def test_encode_and_decode(self):
        steg.encode(medium_filename=self.medium, message_filename="./test/files/test.txt", hidden_filename=self.encoded)
        steg.decode(filename=self.encoded+".png", output_name=self.decoded)
        with open("./test/files/test.txt") as f1, open(self.decoded+".txt") as f2:
            self.assertEqual(list(f1), list(f2), "The files are not equal")
    
    def test_encode_and_decode_encrypted(self):
        steg.encode(medium_filename=self.medium, message_filename="./test/files/test.txt", hidden_filename=self.encoded, key=self.key)
        steg.decode(filename=self.encoded+".png", output_name=self.decoded, key=self.key)
        with open("./test/files/test.txt") as f1, open(self.decoded+".txt") as f2:
            self.assertEqual(list(f1), list(f2), "The files are not equal")

    def test_encode_and_decode_encrypted_without_decrypt(self):
        steg.encode(medium_filename=self.medium, message_filename="./test/files/test.txt", hidden_filename=self.encoded, key=self.key)
        with self.assertRaises(ValueError):
            steg.decode(filename=self.encoded+".png", output_name=self.decoded)

    def tearDown(self):
        shutil.rmtree(self.temp_folder)
