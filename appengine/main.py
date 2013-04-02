import webapp2
from google.appengine.api import users
import os
import jinja2
import logging
from models import Person

from google.appengine.api import search

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    for index in search.get_indexes(fetch_schema=True):
      logging.info("index %s", index.name)
      logging.info("schema: %s", len(index.schema))
    template_values = {'user': user}
    #Site is under maintaince
    #template = jinja_environment.get_template('html/index.html')
    template = jinja_environment.get_template('html/maintenance.html')
    self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication([('/', MainPage)])