import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.api import mail
import logging
import cgi
import urllib
from models import StatsObject
import json

class StatsApi(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    search_query = str(urllib.unquote(cgi.escape(self.request.get('q')).lower()[:100]))

    if search_query == "":
      d = {}
      d['data'] = []
      d['token'] = token
      d['q'] = ""
      s = json.dumps(d)
      self.response.out.write(s)
      return
      
    queries = map(str, search_query.split())
    queries = sorted(queries)
    
    d = {}
    
    for query in queries:
      ob = StatsObject.get_by_id(query)
      if ob:
        d[query] = ob.json
      else:
        d[query] = ''
        
    s = json.dumps(d)
    self.response.out.write(s)


app = webapp2.WSGIApplication([
    ("/stats_api", StatsApi)
  ])

