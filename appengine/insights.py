import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template
import logging
from models import Person
import hashlib
import urllib


class Stats(webapp2.RequestHandler):
  def get(self):
    number_claimed = Person.query(Person.linked_account != None).count()
    unclaimed = Person.query().count(limit=15000) - number_claimed
    template_values = {'active': 'stats',
                       'number_claimed': number_claimed,
                       'unclaimed': unclaimed}
    path = os.path.join(os.path.dirname(__file__), 'html/stats.html')
    self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/insights.*', Stats)])