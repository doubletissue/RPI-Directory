from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import rdbms
from google.appengine.api import memcache
import logging
import cgi
import urllib
from models import Person
from django.utils import simplejson as json

_INSTANCE_NAME = 'christianjohnson.org:rpidirectory:christianjohnson'

class NewApi(webapp.RequestHandler):
  pass

class Api(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year      = urllib.unquote(cgi.escape(self.request.get('year')).lower()[:50])
    major     = urllib.unquote(cgi.escape(self.request.get('major')).lower()[:50])
    name      = urllib.unquote(cgi.escape(self.request.get('name')).lower()[:50])
    token     = urllib.unquote(cgi.escape(self.request.get('token')))
    page_num  = urllib.unquote(cgi.escape(self.request.get('page_num')))
    page_size = urllib.unquote(cgi.escape(self.request.get('page_size')))
    
    
    conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
    cursor = conn.cursor()
    
    names = map(str, name.split()[:3])

    #Get the first name and the last name. Ignore other things.
    if len(names) == 1:
      name_part = '%' + names[0] + '%'
      cursor.execute("SELECT first_name, last_name, major, email, year FROM rpidirectory WHERE first_name LIKE %s OR last_name LIKE %s", (name_part, name_part))
      
    elif len(names) > 1:
      first_name = '%' + names[0] + '%'
      last_name = '%' + names[-1] + '%'
      cursor.execute("SELECT first_name, last_name, major, email, year FROM rpidirectory WHERE first_name LIKE %s AND last_name LIKE %s", (first_name, last_name))
    
    d = {}
    l = []
    
    if len(names) != 0:
      for row in cursor.fetchall():
        l.append({"name": cgi.escape(row[0]) + " " + cgi.escape(row[1]), 
                  "major": cgi.escape(row[2]),
                  "email": cgi.escape(row[3]),
                  "year": cgi.escape(row[4])})
    
    d = {}
    d['data'] = l
    d['token'] = token
    d['name'] = name
    s = json.dumps(d)
    self.response.out.write(s)

application = webapp.WSGIApplication([
    ("/api", Api)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()