import webapp2
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import random
import sys
from models import Person
from emailer import send_activation_email

class Dashboard(webapp2.RequestHandler):
  def get(self):
    # Check if signed in
    user = users.get_current_user()
    rcsid_claim = self.request.get("rcsid_claim", None)
    activation_code = self.request.get("activation", None)
    person = Person.query(Person.linked_account == user).get()

    if user and person:
      self.redirect('/detail/' + person.rcsid)
      return
    elif rcsid_claim:
      if not user:
        self.redirect(users.create_login_url(self.request.uri))
        return
      #Generate code and send email
      code = str(random.randrange(sys.maxint))
      item = {'code': code, 'rcsid': rcsid_claim}
      if not memcache.add(str(user.user_id()), item, 86400):
        message = 'Already sent activation, please check your email.'
      else:
        person = Person.get_by_id(rcsid_claim)
        if person:
          logging.info('Sent email to link %s and %s' % (user.email(), person.rcsid))
          send_activation_email(person, code)
          message = 'Sent activation email to: %s, please check that email.' % (person.email)
        else:
          message = 'Invalid RCS ID: %s...' % (rcsid_claim)
    elif user and activation_code:
      #Check if already exisiting code
      item = memcache.get(str(user.user_id()))
      if item is not None and item['code'] == activation_code:
        person = Person.get_by_id(item['rcsid'])
        person.linked_account = user
        person.put()
        self.redirect('/detail/' + person.rcsid)
        return
    else:
      #Not signed in, offer instructions
      message = None

    template_values = {"active": "dashboard", "message": message}
    path = os.path.join(os.path.dirname(__file__), 'html/activate.html')
    self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/dashboard', Dashboard)])