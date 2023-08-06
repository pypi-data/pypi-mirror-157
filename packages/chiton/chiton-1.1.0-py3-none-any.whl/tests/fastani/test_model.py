from unittest import TestCase

from chiton.fastani.model import FastANIResult


class TestModel(TestCase):

    def test_fastani_result_eq(self):
        a = FastANIResult(ani=89.1234, n_frag=123, total_frag=444)
        b = FastANIResult(ani=89.1234, n_frag=123, total_frag=444)
        c = FastANIResult(ani=89.1234, n_frag=222, total_frag=444)

        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
