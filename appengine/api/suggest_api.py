import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.api import mail
import logging
import cgi
import urllib
from models import SuggestObject
import json

class SuggestApi(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    search_query = str(urllib.unquote(cgi.escape(self.request.get('q')).lower()[:200]))

    if search_query == "":
      d = {}
      d['data'] = []
      d['token'] = token
      d['q'] = ""
      s = json.dumps(d)
      self.response.out.write(s)
      return
      
    r = SuggestObject.get_by_id(search_query)
    
    if r:
      d = {search_query:r.json}
    else:  
      queries = map(str, search_query.split())
    
      d = {}
    
      for query in queries:
        ob = SuggestObject.get_by_id(query)
        if ob:
          d[query] = ob.json
        else:
          d[query] = ''
        
    s = json.dumps(d)
    self.response.out.write(s)


app = webapp2.WSGIApplication([
    ("/suggest_api", SuggestApi)
  ])

