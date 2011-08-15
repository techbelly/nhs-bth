#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import gaeunit

import scrape
import oneoffs

URLS = [
        ('/admin/article_scrape', scrape.article_scraper),
        ('/admin/rescrape', scrape.scrape_unscraped),
        ('/admin/list_scrape', scrape.list_scraper),
        ('/admin/link_stamper', oneoffs.link_stamper)
]

TEST_URLS = [
        ('/test/all', gaeunit.MainTestPageHandler),
        ('/test/run', gaeunit.JsonTestRunHandler),
        ('/test/list', gaeunit.JsonTestListHandler)
]

def main():
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
        application = webapp.WSGIApplication(URLS + TEST_URLS, debug=True)
    else:
        application = webapp.WSGIApplication(URLS)

    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
