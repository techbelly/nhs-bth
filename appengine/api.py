from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache

import simplejson

import models
import utils

class link_syncer(webapp.RequestHandler):
    def get(self):
        
        latest_hash = self.request.get("latest",None)
        if not latest_hash:
            link = models.Link.gql("ORDER BY date_added ASC").get()
            latest_hash = link.key().name()
        else:
            link = models.Link.get_by_key_name(latest_hash)
        
        as_json = memcache.get(latest_hash)
        batch_size = 200
        if as_json is None:
            q = models.Link.gql("WHERE date_added > :1 ORDER BY date_added ASC", link.date_added)
            newer_links = q.fetch(batch_size)
            def clean(l):
                return l.key().name()
            links = map(clean, newer_links)
            as_json = simplejson.dumps(links)
            keep_time = 60 * 60
            if len(links) == batch_size:
                # this batch is cooked.
                keep_time = 0

            memcache.add(latest_hash,as_json,keep_time)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(as_json)

class article_handler(webapp.RequestHandler):
    def get(self):
        response = []

        article_hash = self.request.get("hash")
        page_url = self.request.get("url")

        if page_url and not article_hash:
            article_hash = utils.sha1_hash(page_url)

        if article_hash:
            article = models.Article.from_hash(article_hash)
            if article:
                response.append(article.as_dict())
        
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(simplejson.dumps(response))

application = webapp.WSGIApplication(
[
    ('/article', article_handler),
    ('/link_hashes', link_syncer)
])

def main():
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
