import webapp2
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import random
import sys
import operator
from models import Person
from emailer import send_activation_email

admins = ['christian@christianjohnson.org',
          'jewishdan18@gmail.com',
          'michorowitz@gmail.com']

class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    login_url_linktext = "My Profile"
    if user:
      login_url = '/dashboard'
    else:
      login_url = users.create_login_url("/")
    template_values = {"login_url": login_url,
                       "login_url_linktext": login_url_linktext}
    path = os.path.join(os.path.dirname(__file__), 'html/index_new.html')
    self.response.out.write(template.render(path, template_values))


class DetailPage(webapp2.RequestHandler):
  def get(self, rcs_id):
    logging.error('RCSID: ' + rcs_id)
    user = users.get_current_user()
    login_url_linktext = "My Account"
    if user:
      login_url = users.create_logout_url("/")
      show_dashboard_link = True
    else:
      login_url = users.create_login_url("/")
      show_dashboard_link = False
    template_values = {"rcs_id": rcs_id,
                       "person": Person.get_by_id(rcs_id),
                       "login_url": login_url,
                       "login_url_linktext": login_url_linktext,
                       "show_dashboard_link": show_dashboard_link}
    path = os.path.join(os.path.dirname(__file__), 'html/detail.html')
    self.response.out.write(template.render(path, template_values))

class Dashboard(webapp2.RequestHandler):
  def get(self):
    message = 'Not sure what you are doing here!'
    # Check if signed in
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
    
    rcsid_claim = self.request.get("rcsid_claim", None)
    activation_code = self.request.get("activation", None)
    person = Person.query(Person.linked_account == user).get()
    
    #If person has linked account, redirect to their profile.
    if person:
      self.redirect('/detail/' + person.rcsid)

    if rcsid_claim:
      #Generate code and send email
      code = str(random.randrange(sys.maxint))
      item = {'code': code, 'rcsid': rcsid_claim}
      if not memcache.add(str(user.user_id()), item, 86400):
        message = 'Already sent activation, please check your email.'
      else:
        logging.info('Linking %s and %s' % (user.user_id(), rcsid_claim))
        person = Person.get_by_id(rcsid_claim)
        if person:
          send_activation_email(person, code)
          message = 'Sent activation email to: %s, please check that email.' % (person.email)
        else:
          message = 'Invalid RCS ID: %s...' % (rcsid_claim)
    
    logging.info('HELLO')
    if activation_code:
      #Check if already exisiting code
      item = memcache.get(str(user.user_id()))
      if item is not None and item['code'] == activation_code:
        person = Person.get_by_id(item['rcsid'])
        person.linked_account = user
        person.put()
        self.redirect('/detail/' + person.rcsid)

    template_values = {"message": message}
    path = os.path.join(os.path.dirname(__file__), 'html/activate.html')
    self.response.out.write(template.render(path, template_values))

class UploadProfilePic(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if user:
      if user.email() in admins:
        #Allow picture replacement for admins
        person = Person.get_by_id(self.request.get('rcsid'))
      else:
        person = Person.query(Person.linked_account == user).get()
      if person:
        person.picture = images.resize(self.request.get('file'), 150, 150)
        person.put()
        logging.debug('Uploaded Picture: ' + person.rcsid)
        return
    
class Image(webapp2.RequestHandler):
  def get(self):
    person = Person.get_by_id(self.request.get('rcsid'))
    if person:
      self.response.headers['Content-Type'] = 'image/png'
      self.response.out.write(person.picture)
    else:
      self.error(404)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/dashboard', Dashboard),
                               ('/detail/([^/]+)', DetailPage),
                               ('/upload_picture', UploadProfilePic),
                               ('/picture', Image)])