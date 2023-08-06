import gc
import os
import resource
import unittest
from ..html import html_to_article, fragment_to_text


class TestHtmlToArticle(unittest.TestCase):
    def test_comment(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_article', 'comment_no_space.html'), 'rt') as f:
            without_space = html_to_article(f.read(), 'ru')
        with open(os.path.join(os.path.dirname(__file__), 'html_to_article', 'comment_space.html'), 'rt') as f:
            with_space = html_to_article(f.read(), 'ru')
        with open(os.path.join(os.path.dirname(__file__), 'html_to_article', 'comment_ground.html'), 'rt') as f:
            comment_ground = f.read()

        self.assertEqual(with_space, without_space)
        self.assertEqual(without_space, comment_ground)

    # def test_memory(self):
    #     with open(os.path.join(os.path.dirname(__file__), 'html_to_article', 'page_source.html'), 'rt') as f:
    #         source = f.read()
    #
    #     result = html_to_article(source, 'ru')
    #     memory_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    #     for _ in range(100):
    #         result = html_to_article(source, 'ru')
    #     memory_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    #
    #     self.assertGreater(len(result), 0)
    #     self.assertGreater(memory_start * 1.01, memory_end)


class TestFragmentToText(unittest.TestCase):
    def test_break(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'break_source.html'), 'rt') as f:
            without_space = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'break_ground.txt'), 'rt') as f:
            comment_ground = f.read()

        self.assertEqual(without_space, comment_ground)

    def test_comment(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'comment_no_space.html'), 'rt') as f:
            without_space = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'comment_space.html'), 'rt') as f:
            with_space = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'comment_ground.txt'), 'rt') as f:
            comment_ground = f.read()

        self.assertEqual(with_space, without_space)
        self.assertEqual(without_space, comment_ground)

    def test_article_1(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article1_no_space.html'), 'rt') as f:
            without_space = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article1_space.html'), 'rt') as f:
            with_space = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article1_ground.txt'), 'rt') as f:
            comment_ground = f.read()

        self.assertEqual(with_space, without_space)
        self.assertEqual(without_space, comment_ground)

    def test_article_2(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article2_source.html'), 'rt') as f:
            source = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article2_ground.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_article_3(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article3_source.html'), 'rt') as f:
            source = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article3_ground.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_article_4(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article4_source.html'), 'rt') as f:
            source = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article4_ground.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_empty(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'empty_source.html'), 'rt') as f:
            source = fragment_to_text(f.read())
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'empty_ground.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_memory(self):
        with open(os.path.join(os.path.dirname(__file__), 'fragment_to_text', 'article1_space.html'), 'rt') as f:
            source = f.read()

        result = fragment_to_text(source)
        memory_start = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        for _ in range(100):
            result = fragment_to_text(source)
        gc.collect()
        memory_end = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        self.assertGreater(len(result), 0)
        self.assertGreater(memory_start * 1.05, memory_end)


class TestHtmlToText(unittest.TestCase):
    def test_drive2(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'drive2.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'drive2.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_gazeta(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'gazeta.html'), 'rb') as f:
            source = f.read().decode('cp1251')
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'gazeta.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_habr(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'habr.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'habr.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_kinopoisk(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'kinopoisk.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'kinopoisk.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_kommersant(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'kommersant.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'kommersant.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_kp(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'kp.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'kp.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_lenta(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'lenta.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'lenta.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_livejournal1(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'livejournal1.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'livejournal1.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_livejournal2(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'livejournal2.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'livejournal2.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_livejournal3(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'livejournal3.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'livejournal3.txt'), 'rt') as f:
            ground = f.read()

        # with open(os.path.join(os.path.dirname(__file__), 'html_to_text', '_debug_0.txt'), 'wt') as f:
        #     f.write(source)

        self.assertEqual(ground, source)

    def test_mk(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'mk.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'mk.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_rbc(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'rbc.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'rbc.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_ria(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'ria.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'ria.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_sport(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'sport.html'), 'rb') as f:
            source = f.read().decode('cp1251')
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'sport.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_vc(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'vc.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'vc.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_woman(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'woman.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'woman.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)

    def test_zen(self):
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'zen.html'), 'rt') as f:
            source = f.read()
            source = fragment_to_text(html_to_article(source, 'ru'))
        with open(os.path.join(os.path.dirname(__file__), 'html_to_text', 'zen.txt'), 'rt') as f:
            ground = f.read()

        self.assertEqual(ground, source)
