import webapp2
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
from models import Person

admins = ['christian@christianjohnson.org',
          'jewishdan18@gmail.com',
          'michorowitz@gmail.com']

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

app = webapp2.WSGIApplication([('/upload_picture', UploadProfilePic),
                               ('/picture', Image)])