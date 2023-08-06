from unittest import TestCase

from chiton.fastani.util import validate_paths


class TestValidate(TestCase):

    def test_transform_input_string(self):
        self.assertEqual(frozenset(['/tmp/a.txt']), validate_paths('/tmp/a.txt'))

    def test_transform_input_collection(self):
        data = ['/tmp/a.txt', '/tmp/b.txt', '/tmp/a.txt']
        self.assertEqual(frozenset(data), validate_paths(data))
