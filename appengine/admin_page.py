from google.appengine.api import memcache
from models import Person
from models import SearchPosition
import json
import urllib
import jinja2
import os
import logging
import cgi
import webapp2

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class AdminPage(webapp2.RequestHandler):
  def get(self):

    flush_cache = urllib.unquote(cgi.escape(self.request.get('flushcache')).lower()[:50])
    reset_pos = urllib.unquote(cgi.escape(self.request.get('resetpos')).lower()[:50])
    get_stats = urllib.unquote(cgi.escape(self.request.get('getstats')).lower()[:50])

    if flush_cache:
      if not memcache.flush_all():
        logging.error("Error flushing memcache")
    if reset_pos:
      memcache.set("index", 1, 86400)
      SearchPosition(key_name="index", position=1).put()

    if get_stats:
      d = memcache.get_stats()
      #index = memcache.get("index")
      #if index:
        #d['indexmc'] = index
      #else:
        #d['indexmc'] = -1
      index_from_ds = SearchPosition.get_by_key_name("index")
      if index_from_ds:
        d['indexds'] = index_from_ds.position
      else:
        d['indexds'] = -1
      s = json.dumps(d)
      self.response.out.write(s)
    else:
      template_values = {}
      template = jinja_environment.get_template('html/admin_page.html')
      self.response.out.write(template.render(template_values))


app = webapp2.WSGIApplication(
  [('/admin_page', AdminPage)]
  )
