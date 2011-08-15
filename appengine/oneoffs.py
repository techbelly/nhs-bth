import logging

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.api.labs import taskqueue
import os
from google.appengine.ext.webapp import template

import config
import models
import parsers
import utils

import urllib

class link_stamper(webapp.RequestHandler):
    
    def get(self):
        link = self.request.get('link', None)
        if link is None:
            # First request, just get the first name out of the datastore.
            model = models.Link.gql('ORDER BY link DESC').get()
            link = model.link

        q = models.Link.gql('WHERE link <= :1 ORDER BY link DESC', link)
        
        links = q.fetch(limit=2)
        current_link = links[0]
        
        if len(links) == 2:
            next_link = links[1].link
            next_url = '/admin/link_stamper?link=%s' % urllib.quote(next_link)
        else:
            next_link = 'FINISHED'
            next_url = '/'  # Finished processing, go back to main page.
        # In this example, the default values of 0 for num_votes and avg_rating are
        # acceptable, so we don't need to do anything other than call put().
        current_link.put()

        context = {
            'current_link': link,
            'next_link': next_link,
            'next_url': next_url,
        }
        self.response.out.write(template.render('templates/link_stamper.html', context))