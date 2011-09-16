from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import logging
import cgi
import urllib
from models import Person
from django.utils import simplejson as json

class Api(webapp.RequestHandler):
  
  def nameSearch(self,name_type,name,year,major, num_results, page_offset):
    logging.debug("Searching for " + name_type + " of " + name)
    result = memcache.get(name_type + ":" + name + ":" + year + ":" + major)
    if result:
      logging.debug("cache hit")
      # Reset the timer
      #if not memcache.set(name_type + ":" + name + ":" + year + ":" + major, result, 86400):
        #logging.error("Memcache set failed.")
        
      if len(result) > 0:
        logging.debug("Got " + str(len(result)) + " results, returning")
        return result, True
      else:
        logging.debug("Got " + str(len(result)) + " results, recurring to " + name[:-1])
        results,_ = self.nameSearch(name_type,name[:-1],year,major,num_results,page_offset)
        return results, False
    
    
    if name == '':
      return [], True
    
    query = Person.all()
    
    if year is not "":
      query = query.filter('year = ',year)
    if major is not "":
      query = query.filter('major = ',major)
    
    query = query.filter(name_type + ' >= ', name)
    query = query.filter(name_type + ' <= ', name+u'\ufffd')
    query = query.order(name_type)
    results = query.fetch(num_results)
    
    modded = False
    
    if len(results) == 0:
      modded = True
      results,_ = self.nameSearch(name_type,name[:-1],year,major,num_results,page_offset)
    if not memcache.set(name_type + ":" + name + ":" + year + ":" + major, results, 86400):
      logging.error("Memcache set failed.")
    else:
      logging.debug("Memcache success with " + str(len(results)))
      
      result = memcache.get(name_type + ":" + name + ":" + year + ":" + major)
      if result:
        logging.debug("Got " + str(len(results)))
      else:
        logging.debug("FAILED")

    return results, modded
    
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year  = urllib.unquote( cgi.escape(self.request.get('year' )).lower()[:50] )
    major = urllib.unquote( cgi.escape(self.request.get('major')).lower()[:50] )
    name  = urllib.unquote( cgi.escape(self.request.get('name' )).lower()[:50] )
    token = urllib.unquote( cgi.escape(self.request.get('token'))              )
    
    names = name.split()[:3]
    
    l = []
    
    if len(names) == 1:
      first_name_results, modded = self.nameSearch('first_name',names[0],year,major, 1000, 0)
      for p in first_name_results:
        l.append(Person.buildMap(p))
      last_name_results, modded  = self.nameSearch('last_name',names[0],year,major, 1000, 0)
      for p in last_name_results:
        l.append(Person.buildMap(p))
    elif len(names) > 1:
      d = set()
      last_name_results, modded = self.nameSearch('last_name',names[-1],year,major, 1000, 0)
      for p in last_name_results:
        d.add(p.key().name())
      first_name_results, modded  = self.nameSearch('first_name',names[0],year,major, 1000, 0)
      i = 0
      for p in first_name_results:
        if p.key().name() in d:
          l.append(Person.buildMap(p))
          i += 1
          if i > 20:
            break
    
    l = sorted(l, key=lambda person: person['name'])
    l = l[:20]
    d = {}
    d['data'] = l
    d['token'] = token
    s = json.dumps(d)
    self.response.out.write(s)
    

application = webapp.WSGIApplication(
  [
    ("/api", Api)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()