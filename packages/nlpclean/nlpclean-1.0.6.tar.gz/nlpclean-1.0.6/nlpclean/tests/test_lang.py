import os
import unittest
from ..lang import detect_main_lang


class TestDetectMainLang(unittest.TestCase):
    def test_unknown(self):
        lang, reliable, score = detect_main_lang('')

        self.assertEqual(lang, 'en')
        self.assertEqual(reliable, False)
        self.assertAlmostEqual(score, 0.1399554025874619, places=5)

    def test_short(self):
        lang, reliable, score = detect_main_lang('Ну')

        self.assertEqual(lang, 'ru')
        self.assertEqual(reliable, False)
        self.assertAlmostEqual(score, 0.7520208358764648, places=5)

    def test_english(self):
        with open(os.path.join(os.path.dirname(__file__), 'detect_main_lang', 'english.txt'), 'rt') as f:
            lang, reliable, score = detect_main_lang(f.read())

        self.assertEqual(lang, 'en')
        self.assertEqual(reliable, True)
        self.assertAlmostEqual(score, 0.9850196492671967, places=5)

    def test_russian(self):
        with open(os.path.join(os.path.dirname(__file__), 'detect_main_lang', 'russian.txt'), 'rt') as f:
            lang, reliable, score = detect_main_lang(f.read())

        self.assertEqual(lang, 'ru')
        self.assertEqual(reliable, True)
        self.assertAlmostEqual(score, 0.7877880418300629, places=5)

    def test_bulgarian(self):
        with open(os.path.join(os.path.dirname(__file__), 'detect_main_lang', 'bulgarian.txt'), 'rt') as f:
            lang, reliable, score = detect_main_lang(f.read())

        self.assertEqual(lang, 'bg')
        self.assertEqual(reliable, True)
        self.assertAlmostEqual(score, 0.88753937125206, places=5)

    def test_ukrain(self):
        with open(os.path.join(os.path.dirname(__file__), 'detect_main_lang', 'ukrain.txt'), 'rt') as f:
            lang, reliable, score = detect_main_lang(f.read())

        self.assertEqual(lang, 'uk')
        self.assertEqual(reliable, True)
        self.assertAlmostEqual(score, 0.9597222125530243, places=5)

    def test_combined(self):
        with open(os.path.join(os.path.dirname(__file__), 'detect_main_lang', 'combined.txt'), 'rt') as f:
            lang, reliable, score = detect_main_lang(f.read())

        self.assertEqual(lang, 'uk')
        self.assertEqual(reliable, False)
        self.assertLess(score, 0.5)
