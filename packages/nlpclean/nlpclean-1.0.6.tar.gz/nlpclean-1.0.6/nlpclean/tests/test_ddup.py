import os
import unittest
from ..ddup import dedup_lines_bloom


class TestDedupLinesBloom(unittest.TestCase):
    def test_all_dup(self):
        with open(os.path.join(os.path.dirname(__file__), 'dedup_lines_bloom', 'all_dup_source.txt'), 'rt') as f:
            source = f.read().split('\n')
            result = dedup_lines_bloom(source, just_words=False, zero_digits=False, capacity=10)
            result = list(result)
        with open(os.path.join(os.path.dirname(__file__), 'dedup_lines_bloom', 'all_dup_ground.txt'), 'rt') as f:
            expected = f.read().split('\n')

        self.assertListEqual(expected, result)

    def test_dup_noise(self):
        with open(os.path.join(os.path.dirname(__file__), 'dedup_lines_bloom', 'dup_noise_source.txt'), 'rt') as f:
            source = f.read().split('\n')
            result = dedup_lines_bloom(source, just_words=True, zero_digits=True, capacity=10)
            result = list(result)
        with open(os.path.join(os.path.dirname(__file__), 'dedup_lines_bloom', 'dup_noise_ground.txt'), 'rt') as f:
            expected = f.read().split('\n')

        self.assertListEqual(expected, result)

    def test_some_dup(self):
        with open(os.path.join(os.path.dirname(__file__), 'dedup_lines_bloom', 'some_dup_source.txt'), 'rt') as f:
            source = f.read().split('\n')
            result = dedup_lines_bloom(source, just_words=True, zero_digits=True, capacity=10)
            result = list(result)
        with open(os.path.join(os.path.dirname(__file__), 'dedup_lines_bloom', 'some_dup_ground.txt'), 'rt') as f:
            expected = f.read().split('\n')
        print('\n'.join(result))

        self.assertListEqual(expected, result)
