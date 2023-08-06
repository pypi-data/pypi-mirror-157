import os
import unittest
from ..repair import repair_html_entities, repair_broken_unicode


class TestRepairHtmlEntities(unittest.TestCase):
    def test_single(self):
        source = 'Test&nbsp;me'
        result = repair_html_entities(source)

        self.assertEqual('Test me', result)

    def test_double(self):
        source = 'Test&amp;lt;me'
        result = repair_html_entities(source)

        self.assertEqual('Test<me', result)


class TestRepairBrokenUnicode(unittest.TestCase):
    def test_encoding(self):
        source = 'âœ” No problems'
        result = repair_broken_unicode(source)

        self.assertEqual('✔ No problems', result)

    def test_width(self):
        source = 'ＬＯＵＤ　ＮＯＩＳＥＳ'
        result = repair_broken_unicode(source)

        self.assertEqual('LOUD NOISES', result)
