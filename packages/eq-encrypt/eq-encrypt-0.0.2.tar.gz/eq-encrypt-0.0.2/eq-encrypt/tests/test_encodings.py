from unittest import TestCase
from ..encodings import B64Decrypt


class B64DecryptTest(TestCase):
    def setUp(self):
        self.instance = B64Decrypt()

    def test_encrypt(self):
        expected = 'aG9sYQ=='
        self.assertEqual(expected, self.instance.encrypt('hola'))

    def test_decrypt(self):
        expected = 'hola'
        self.assertEqual(expected, self.instance.decrypt('aG9sYQ=='))
