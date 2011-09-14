from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from models import Person
from models import SearchPosition
import os
from google.appengine.ext.webapp import template
import logging
import cgi


class AdminPage(webapp.RequestHandler):
  def get(self):
    
    flush_cache  = urllib.unquote( cgi.escape(self.request.get('flushcache' )).lower()[:50] )
    reset_pos = urllib.unquote( cgi.escape(self.request.get('resetpos')).lower()[:50] )
    
    if flush_cache:
      if not memcache.flush_all():
        logging.error("Error flushing memcache"
    if reset_pos:
      memcache.set("index", 1, 86400)
      SearchPosition(key_name="index", position=1).put()
      
    
    
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
