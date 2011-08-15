import logging
import os
import sys
import unittest

app_root = os.path.abspath(
        os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, app_root)

import parsers

def parseintodict(file):
    data = open(file).read()
    links = {}
    for type, html, link in parsers.links_in_article(data):
        if not links.has_key(type):
            links[type] = []
        links[type].append((html, link))
    return links

class BasicHTMLParsingTests(unittest.TestCase):
    def setUp(self):
        self.links = parseintodict('test/data/basic.html')

    def each_tuple(self):
        for link in self.links:
            links = self.links[link]
            for tple in links:
                yield tple

    def test_basic_webpage(self):
        "Parser should deliver all the links on the page."
        self.assertEqual(5, len(self.links['headline']))
        self.assertEqual(1, len(self.links['science']))
        self.assertEqual(5, len(self.links['useful']))
        self.assertEqual(5, len(self.links['related']))

    def test_char_encoding(self):
        "Everything delivered should be unicode."
        for html, link in self.each_tuple():
            self.assertEqual(True, isinstance(html, unicode))
            self.assertEqual(True, isinstance(link, unicode))

    def test_relative_links(self):
        "All relative links should be made absolute"
        for html, link in self.each_tuple():
            self.assertTrue(link.startswith("http://"))

    def test_useful_links_should_go_to_nhs(self):
        "Useful links, in particular should go to useful page."
        for html, link in self.links['useful']:
            self.assertTrue(link.startswith("http://www.nhs.uk/"))

class NoScienceHTMLParsingTests(unittest.TestCase):
    "Smoke test to see what happens when there's no science"

    def setUp(self):
        self.links = parseintodict('test/data/no_science.html')

    def test_basic_webpage(self):
        "Parser should not fail when there are no science links."
        self.assertFalse(self.links.has_key('science'))

class NoUsefulHTMLParsingTests(unittest.TestCase):
    "Smoke test  to see what happens when there's no useful"

    def setUp(self):
        self.links = parseintodict('test/data/no_useful.html')

    def test_basic_webpage(self):
        "Parser should not fail when there are no useful links."
        self.assertFalse(self.links.has_key('useful'))

if __name__ == '__main__':
    unittest.main()
