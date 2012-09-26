import webapp2
from google.appengine.api import users
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
    login_url_linktext = "My Account"
    if user:
      login_url = users.create_logout_url("/")
      show_dashboard_link = True
    else:
      login_url = users.create_login_url("/")
      show_dashboard_link = False
    number_people = 11712
    template_values = {"number_people": number_people,
                       "login_url": login_url,
                       "login_url_linktext": login_url_linktext,
                       "show_dashboard_link": show_dashboard_link}
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
    account = Account.get_or_create_current_account()
    person_rcsid = self.request.get("PersonRCS", None)
    activation_code = self.request.get("ActivationCode", None)
    person = account.get_linked_person()

    # If the account is not activated
    if not person:
      if person_rcsid:
        person = Person.gql("WHERE rcsid = :1", person_rcsid).get()
        account.init_linked_person(person)
      if activation_code:
        activation_code = int(activation_code)
        account.activate_person(activation_code)
    self.response.out.write(account.user.email())

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/dashboard', Dashboard),
                               ('/detail/([^/]+)', DetailPage)])