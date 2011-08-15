import datetime
import itertools
import urllib
import urlparse
import logging

from google.appengine.ext import db
from google.appengine.api import urlfetch

import utils
import parsers


class Domain(db.Model):
    name = db.StringProperty()

    @classmethod
    def insert(cls, name):
        key_name = utils.sha1_hash(name)
        domain = Domain.get_by_key_name(key_name)
        if domain is None:
            domain = Domain(key_name=key_name, name=name)
            domain.put()
            return True
        else:
            return False

class Article(db.Model):
    title = db.StringProperty()
    published = db.DateTimeProperty()
    address = db.URLProperty()
    scraped = db.BooleanProperty()

    @staticmethod
    def from_hash(hash):
        link = Link.get_by_key_name(hash)
        if link:
            return link.article
        else:
            return None

    def as_dict(self):
        links = {}
        link_type = lambda x: x.type
        grouped = itertools.groupby(sorted(self.links, key=link_type), link_type)
        for type,group in grouped:
            links[type] = [link.html for link in group]
        return {
            'article': self.title,
            'address': self.address,
            'links': links }

    @classmethod
    def most_recent_article_date(cls):
        articles = Article.all()
        articles.order("-published")
        article = articles.fetch(1)
        if article:
            return article[0].published
        else:
            return datetime.datetime(2007,01,01)

    def add_link(self, html, link, type):
        return Link.insert(html, link, type, self)

    def update_links(self, links):
        found_links = False
        for type, html, link in links:
            self.add_link(html, link, type)
            found_links = True
        if found_links:
            self.scraped = True
            self.put()

    def original_html(self):
        valid_address = urllib.quote(self.address, ':\/')
        return urlfetch.fetch(valid_address).content

    def scrape(self):
        links = parsers.links_in_article(self.original_html())
        self.update_links(links)
        return self.scraped

class Link(db.Model):
    html = db.TextProperty()
    link = db.URLProperty()
    type = db.StringProperty(
            choices=set(['science', 'headline', 'related', 'useful']))
    article = db.ReferenceProperty(Article, collection_name='links')
    date_added = db.DateTimeProperty(auto_now=True)

    @classmethod
    def insert(cls, html, link, type, article):
        key_name = utils.sha1_hash(link)
        found_link = Link.get_by_key_name(key_name)

        if found_link is None:
            url = urlparse.urlparse(link)
            if type == 'headline':
                Domain.insert(url.netloc)
            clean_link = urlparse.urlunparse(url)
            found_link = Link(key_name=key_name, html=html, link=clean_link,
                             type=type, article=article)
            found_link.put()
            return True
        else:
            return False
