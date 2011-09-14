from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Person
import os
from google.appengine.ext.webapp import template
import logging
import cgi


class AdminPage(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'admin_page.html')
    self.response.out.write(template.render(path, template_values))
    
    
application = webapp.WSGIApplication(
  [('/admin_page', AdminPage)]
  )
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
