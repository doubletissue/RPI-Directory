import webapp2
from google.appengine.api import users
import os
import jinja2
import logging
from models import Person
import hashlib
import urllib

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class DetailPage(webapp2.RequestHandler):
  def get(self, rcs_id):
    user = users.get_current_user()
    enabled_user = None
    person = Person.get_by_id(rcs_id)
    if person and person.picture:
      img = 'http://rpidirectory.appspot.com/picture/%s' % (rcs_id)
    else:
      img = 'https://dl.dropbox.com/u/1253608/370556590677.png'
    if user:
      enabled_user = Person.query(Person.linked_account == user).get()
    
    template_values = {"active": "dashboard",
                       "rcs_id": rcs_id,
                       "person": person,
                       "user": user,
                       "enabled_user": enabled_user,
                       "img": img}
    template = jinja_environment.get_template('html/detail.html')
    self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/detail/([^/]+)', DetailPage)])