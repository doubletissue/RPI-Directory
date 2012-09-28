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
    default_img = 'http://rpidirectory.appspot.com/picture/%s.png' % (rcs_id)
    person = Person.get_by_id(rcs_id)
    if person:
      hashed_email = hashlib.md5(person.email.lower()).hexdigest()
      gravatar_url = "http://www.gravatar.com/avatar/" + hashed_email  + "?"
      gravatar_url += urllib.urlencode({
        'd': default_img, 
        's': str(150)}
      )
    else:
      gravatar_url = 'https://s3-eu-west-1.amazonaws.com/assimbli/unknown_profile.jpg'

    if user:
      enabled_user = Person.query(Person.linked_account == user).get()
    
    template_values = {"active": "dashboard",
                       "rcs_id": rcs_id,
                       "person": person,
                       "user": user,
                       "enabled_user": enabled_user,
                       "img": gravatar_url}
    path = os.path.join(os.path.dirname(__file__), 'html/detail.html')
    self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/detail/([^/]+)', DetailPage)])