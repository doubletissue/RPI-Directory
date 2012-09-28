import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template
import logging
from models import Person
import hashlib
import urllib


class DetailPage(webapp2.RequestHandler):
  def get(self, rcs_id):
    user = users.get_current_user()
    enabled_user = None
    person = Person.get_by_id(rcs_id)
    if person and person.picture:
      img = 'http://rpidirectory.appspot.com/picture/%s' % (rcs_id)
    else:
      img = 'http://lh3.googleusercontent.com/16QX8mPZ10EWtlxJ04A9nHNTFA1XrAa4aKOJba5Me_-SXWl-tldF-2WCZX0rjL7nOORe-yJLHHk'
    if user:
      enabled_user = Person.query(Person.linked_account == user).get()
    
    template_values = {"active": "dashboard",
                       "rcs_id": rcs_id,
                       "person": person,
                       "user": user,
                       "enabled_user": enabled_user,
                       "img": img}
    path = os.path.join(os.path.dirname(__file__), 'html/detail.html')
    self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/detail/([^/]+)', DetailPage)])