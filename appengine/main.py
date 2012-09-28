import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template
import logging
from models import Person


class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'html/index_new.html')
    self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([('/', MainPage)])