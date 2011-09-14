from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
import cgi
import urllib
from models import Person
from django.utils import simplejson as json

class Api(webapp.RequestHandler):
  
  def nameSearch(self,name_type,name,year,major, num_results, page_offset):
    query = Person.all()
    
    if year is not "":
      query = query.filter('year = ',year)
    if major is not "":
      query = query.filter('major = ',major)
    
    query = query.filter(name_type + ' >= ', name)
    query = query.filter(name_type + ' <= ', name+u'\ufffd')
      
    
    return query.fetch(num_results)
    
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year  = urllib.unquote( cgi.escape(self.request.get('year' )).lower() )
    major = urllib.unquote( cgi.escape(self.request.get('major')).lower() )
    name  = urllib.unquote( cgi.escape(self.request.get('name' )).lower() )
    
    names = name.split()[:3]
    
    l = []
    
    if len(names) == 1:
      first_name_results = self.nameSearch('first_name',names[0],year,major, 10, 0)
      for p in first_name_results:
        l.append(Person.buildMap(p))
      last_name_results  = self.nameSearch('last_name',names[0],year,major, 10, 0)
      for p in last_name_results:
        l.append(Person.buildMap(p))
    elif len(names) > 1:
      d = set()
      first_name_results = self.nameSearch('first_name',names[0],year,major, 1000, 0)
      for p in first_name_results:
        d.add(p.key().name())
      last_name_results  = self.nameSearch('last_name',names[-1],year,major, 1000, 0)
      i = 0
      for p in last_name_results:
        if p.key().name() in d:
          l.append(Person.buildMap(p))
          i += 1
          if i > 20:
            break
    s = json.dumps(l)
    self.response.out.write(s)
    

application = webapp.WSGIApplication(
  [
    ("/api", Api)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()