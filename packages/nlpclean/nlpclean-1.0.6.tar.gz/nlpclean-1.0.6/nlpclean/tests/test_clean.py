import os
import unittest
from ..clean import remove_accent_glyphs


class TestRemoveAccentGlyphs(unittest.TestCase):
    def test_normal(self):
        source = 'ударе́ние'
        result = remove_accent_glyphs(source)

        self.assertEqual('ударение', result)
