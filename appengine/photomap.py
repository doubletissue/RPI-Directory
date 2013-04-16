import webapp2
from google.appengine.api import users
import os
import jinja2
import logging
from random import shuffle
from models import Person

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Explore(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    
    # Get all users that have a photo
    qry = Person.query(Person.has_picture == True).fetch(100)
    #Shuffle the list around to make it different every time
    shuffle(qry)
    template_values = {'user': user, 'people': qry}
    template = jinja_environment.get_template('html/photomap.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/photomap', Explore)])