import re
from bs4 import BeautifulSoup, Comment
from html import unescape
from lxml import etree
from newspaper.cleaners import DocumentCleaner as BaseNewspaperCleaner
from newspaper.configuration import Configuration as NewspaperConfig
from newspaper.extractors import ContentExtractor as NewspaperExtractor
from newspaper.outputformatters import OutputFormatter as NewspaperFormatter

_MEANINGLESS_TAGS = [
    'applet', 'audio', 'blockquote', 'canvas', 'code', 'comment', 'datalist', 'embed', 'figure', 'form', 'frame',
    'frameset', 'iframe', 'img', 'kbd', 'map', 'menu', 'noembed', 'noframes', 'noscript', 'object', 'output',
    'plaintext', 'pre', 'ruby', 'samp', 'script', 'style', 'svg', 'title', 'var', 'video', 'xmp'
]

_BLOCKLEVEL_TAGS = [
    'address', 'article', 'aside', 'blockquote', 'center', 'dd', 'details', 'dialog', 'dir', 'div', 'dl', 'dt',
    'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr',
    'isindex', 'li', 'main', 'menu', 'nav', 'noframes', 'noscript', 'ol', 'p', 'pre', 'section', 'table', 'td', 'th',
    'tr', 'ul'
]


def html_to_article(content, language):
    content = content.strip()
    if not len(content):
        return ''

    config = NewspaperConfig()
    config.language = language

    doc = config.get_parser().fromstring(content.strip())
    if doc is None:
        return ''

    # Split block-level elements with newlines
    for tag in _BLOCKLEVEL_TAGS:
        if tag in _MEANINGLESS_TAGS:
            continue
        for node in doc.xpath('//{}'.format(tag)):
            node.append(etree.Element('br'))
            node.append(etree.Element('br'))

    # Initial cleanup
    cleaner = _NewspaperCleaner(config)
    doc = cleaner.clean(doc)

    # Best node estimation
    extractor = NewspaperExtractor(config)
    top = extractor.calculate_best_node(doc)
    if top is None:
        del doc, cleaner, extractor
        etree.clear_error_log()

        return ''

    top = extractor.post_cleanup(top)

    # Cleanup dummy nodes used for estimation
    for dummy in top.xpath("//p[@newspaper='dummy']"):
        dummy.getparent().remove(dummy)

    # Custom formatting to avoid unnecessary computations
    formatter = NewspaperFormatter(config)
    formatter.top_node = top
    formatter.remove_negativescores_nodes()
    content = formatter.convert_to_html()
    content = str(content).strip()
    content = unescape(content)

    del doc, top, cleaner, extractor, formatter
    etree.clear_error_log()

    return content


def fragment_to_text(html):
    if not len(html.strip()):
        return ''

    soup = BeautifulSoup(html, 'lxml')
    if soup is None:
        raise ValueError('Can\'t build DOM tree with LXML')

    # Drop comments
    for comment in soup(text=lambda txt: isinstance(txt, Comment)):
        comment.extract()

    # Drop non-meaning tags
    for node in soup(_MEANINGLESS_TAGS):
        node.replace_with(soup.new_tag('br'))

    # Insert linebreaks around block-level tags
    for node in soup(_BLOCKLEVEL_TAGS):
        node.insert_before(soup.new_tag('br'))
        node.insert_before(soup.new_tag('br'))
        node.insert_after(soup.new_tag('br'))
        node.insert_after(soup.new_tag('br'))

    # Remove linebreaks inside text nodes (as browser does)
    for node in soup(string=lambda string: '\n' in string):
        node.string.replace_with(node.string.replace('\n', ' '))

    # Swap html linebreaks to normal ones
    for node in soup('br'):
        node.replace_with('\n')

    # Cleanup final text
    text = soup.getText()
    text = str(text).strip()
    text = re.sub(' {2,}', ' ', text)
    text = text.replace(' \n', '\n').replace('\n ', '\n')
    text = re.sub('\n{3,}', '\n\n', text)

    soup.decompose()
    etree.clear_error_log()
    del soup

    return text


class _NewspaperCleaner(BaseNewspaperCleaner):
    def clean(self, doc_to_clean):
        doc_to_clean = super(_NewspaperCleaner, self).clean(doc_to_clean)

        doc_to_clean = self.div_to_para(doc_to_clean, 'article')

        return doc_to_clean

    def div_to_para(self, doc, dom_type):
        if 'span' == dom_type:
            return doc

        tags = ['a', 'blockquote', 'dl', 'div', 'img', 'ol', 'p', 'pre', 'table', 'ul']
        divs = self.parser.getElementsByTag(doc, tag=dom_type)
        for div in divs:
            items = self.parser.getElementsByTags(div, tags)
            if div is not None and len(items) == 0:
                self.replace_with_para(doc, div)
            elif div is not None:
                self.make_dummy_kid(doc, div)

        return doc

    def make_dummy_kid(self, doc, div):
        text_to_return = []
        replacement_text = []

        if div.text:
            replacement_text.append(div.text.strip())

        for kid in div:
            # The node is a <p> and already has some replacement text
            if self.parser.getTag(kid) == 'p' and len(replacement_text) > 0:
                text_to_return.append(' '.join(replacement_text))
                replacement_text = []
            # The node is a text node
            elif self.parser.getTag(kid) == 'a':
                kid_text = self.parser.outerHtml(kid)
                replacement_text.append(kid_text.strip())

            # The node is a text node
            if kid.tail:
                replacement_text.append(kid.tail.strip())

        # Flush out anything still remaining
        if len(replacement_text):
            text_to_return.append(' '.join(replacement_text))

        for node in text_to_return:
            if not len(node.strip()):
                continue

            node = self.get_flushed_buffer(node, doc)
            if node is None:
                continue

            node.attrib['newspaper'] = 'dummy'
            div.append(node)
