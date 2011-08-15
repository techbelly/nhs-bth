import logging

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue

import config
import models
import parsers
import utils

def schedule_scraping(article):
    taskqueue.add(url='/admin/article_scrape', params={'article':article.key()},
                  method='GET')

def schedule_list_scraping(since, page):
    params = {"page": str(page), "since": utils.to_isodate(since)}
    taskqueue.add(url='/admin/list_scrape', params=params, method='GET')

BATCH_SIZE = 10
def create_url(page, user, password):
    return "http://www.nhs.uk/NHSCWS/News/NewsArticlesList.aspx" +\
           "?user=%s&pwd=%s&pageNumber=%d&pageSize=%d" % (
           user, password, page, BATCH_SIZE)

def log_and_output(response,message):
    response.out.write(message)
    logging.info(message)

class list_scraper(webapp.RequestHandler):

    def param(self,name,transformer,default=None):
        p = self.request.get(name)
        if p:
            p = transformer(p)
        else:
            p = default
        return p

    def scrape_articles(self, page):
        response = urlfetch.fetch(create_url(page, config.user, config.password))
        all_articles = parsers.articles_from_xml(response.content)
        return all_articles

    def get(self):
        page = self.param("page",int,default=1)
        since = self.param("since", utils.isodate)
        if not since:
            since = models.Article.most_recent_article_date()

        new_articles = 0
        for link, date, title in self.scrape_articles(page=page):
            if date > since:
                art = models.Article(title=title, published=date, address=link,
                                     scraped=False)
                art.put()
                new_articles += 1
                schedule_scraping(art)

        log_and_output(self.response,"Queued %d articles for scraping" % new_articles)

        if new_articles == BATCH_SIZE:
            schedule_list_scraping(since, page + 1)

class article_scraper(webapp.RequestHandler):
    def get(self):
        article_key = self.request.get("article")
        article = models.Article.get(article_key)
        if article.scraped:
            log_and_output(self.response,"Article already scraped")
        else:
            if article.scrape():
                log_and_output(self.response,"Scraped article, all good")

class scrape_unscraped(webapp.RequestHandler):
    def get(self):
        articles = models.Article.all()
        articles.filter("scraped =", False)
        added = 0
        for art in articles.fetch(10):
            schedule_scraping(art)
            added += 1
        log_and_output(self.response,"Queued %d articles for scraping" % added)


