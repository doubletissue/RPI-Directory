import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import operator


class MainPage(webapp2.RequestHandler):
  def get(self):
    number_people = 11712
    template_values = {"number_people": number_people}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/', MainPage)])