import webapp2
from google.appengine.api import users
import os
import jinja2
import logging
from models import Person
from models import StatsObject

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Explore(webapp2.RequestHandler):
  def get(self):    
    template_values = {'active': 'explore'}

    template = jinja_environment.get_template('html/explore.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/explore', Explore)])