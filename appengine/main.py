from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from models import Person
import os
from google.appengine.ext.webapp import template
import logging
import cgi


class MainPage(webapp.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class Search(webapp.RequestHandler):
  def post(self):
    results = Person.all().filter(first_name=keyword).fetch(100)
    template_values = {
      'results': results,
    }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
  [('/search', Search),
   ('/', MainPage),])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
