import webapp2
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import operator
from models import Account
from models import Person

class MainPage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    login_url_linktext = "Claim Account"
    if user:
      login_url = '/dashboard'
      login_url_linktext = "My Account"
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
    # Check if signed in
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))

    account = Account.get_or_create_current_account()
    person_rcsid = self.request.get("rcsid_claim", None)
    activation_code = self.request.get("activate", None)
    if account:
      person = account.get_linked_person()
    else:
      person = None

    message = 'Signed in as %s, please goto a profile to claim it.' % (user.nickname())

    # If the account is not activated
    if not person:
      if person_rcsid:
        person = Person.gql("WHERE rcsid = :1", person_rcsid).get()
        account.init_linked_person(person)
        #Send email
        message = 'Sent email to: %s, please click the link in the email' % (person.email)
      if activation_code:
        activation_code = int(activation_code)
        account.activate_person(activation_code)
        #Activated Person
        message = 'Your account has been activated!'
    template_values = {"message": message}
    path = os.path.join(os.path.dirname(__file__), 'html/activate.html')
    self.response.out.write(template.render(path, template_values))

class UploadProfilePic(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    if user:
      account = Account.get_by_user(user)
      person = account.get_linked_person().get()
      if person:
        person.picture = images.resize(self.request.get('file'), 150, 150)
        person.put()
        logging.debug('Uploaded Picture: ' + person.rcsid)
        return
    #logging.debug('Tried to upload...failed.')
    #person = Person.get_by_id('johnsc12')
    #person.picture = images.resize(self.request.get('file'), 150, 150)
    #person.put()
    #logging.debug('Uploaded Picture!')
    
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