from unittest import TestCase

from chiton.fastani.config import FastAniVersion
from chiton.fastani.version import get_fastani_version


class TestVersion(TestCase):

    def test_get_version(self):

        for v in FastAniVersion:
            if v is FastAniVersion.v1_1_or_1_2:
                self.assertTrue(get_fastani_version('fastANI_1.1') is FastAniVersion.v1_1_or_1_2)
                self.assertTrue(get_fastani_version('fastANI_1.2') is FastAniVersion.v1_1_or_1_2)
            else:
                self.assertTrue(get_fastani_version(f'fastANI_{v.value}') is v)
