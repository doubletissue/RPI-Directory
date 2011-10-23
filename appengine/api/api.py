from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import logging
import cgi
import urllib
from models import Person
from django.utils import simplejson as json


class NewApi(webapp.RequestHandler):
  pass

class Api(webapp.RequestHandler):
  
  def nameSearch(self,name_type,name,year,major, num_results, page_offset):
    logging.debug("Searching for " + name_type + " of " + name)
    cache = memcache.get(name_type + ":" + name + ":" + year + ":" + major)
    if cache:
      logging.debug("Number of items from cache: " + str(cache))
      result,recursion_level = cache
      if result:
        logging.debug("cache hit, recur level ofs " + str(recursion_level))
        # Reset the timer
        #if not memcache.set(name_type + ":" + name + ":" + year + ":" + major, result, 86400):
          #logging.error("Memcache set failed.")
          
        logging.debug("Got " + str(len(result)) + " results, returning")
        return result, recursion_level
    
    
    if name == '':
      return [], 0
    
    query = Person.all()
    
    if year is not "":
      query = query.filter('year = ',year)
    if major is not "":
      query = query.filter('major = ',major)
    
    query = query.filter(name_type + ' >= ', name)
    query = query.filter(name_type + ' <= ', name+u'\ufffd')
    query = query.order(name_type)
    results = query.fetch(num_results)
    
    recursion_level = 0
    
    if len(results) == 0:
      results,recursion_level = self.nameSearch(name_type,name[:-1],year,major,num_results,page_offset)
      recursion_level += 1
    if not memcache.set(name_type + ":" + name + ":" + year + ":" + major, (results,recursion_level), 86400):
      logging.error("Memcache set failed.")

    return results, recursion_level
    
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year  = urllib.unquote(cgi.escape(self.request.get('year')).lower()[:50])
    major = urllib.unquote(cgi.escape(self.request.get('major')).lower()[:50])
    name  = urllib.unquote(cgi.escape(self.request.get('name')).lower()[:50])
    token = urllib.unquote(cgi.escape(self.request.get('token')))
    
    names = name.split()[:3]
    
    quick_person = Person.get_by_key_name(names[0])
    
    l1 = []
    l2 = []
    l = []
    
    if len(names) == 1:
      first_name_results, first_name_recur = self.nameSearch('first_name',names[0],year,major, 1000, 0)
      for p in first_name_results[:20]:
        l1.append(Person.buildMap(p))
      last_name_results, last_name_recur  = self.nameSearch('last_name',names[0],year,major, 1000, 0)
      for p in last_name_results[:20]:
        l2.append(Person.buildMap(p))
      
      first_name_quantity = 20*len(first_name_results)/(len(first_name_results)+len(last_name_results))
      last_name_quantity = 20*len(last_name_results)/(len(first_name_results)+len(last_name_results))
      if first_name_recur == last_name_recur:
        l1 = l1[:first_name_quantity]
        l2 = l2[:last_name_quantity]
      elif first_name_recur < last_name_recur:
        l2 = []
      elif first_name_recur > last_name_recur:
        l1 = []
        
      l = l1
      l.extend(l2)
      l = sorted(l, key=lambda person: person['name'])[:20]
      
    elif len(names) > 1:
      d = set()
      last_name_results, first_name_recur = self.nameSearch('last_name',names[-1],year,major, 1000, 0)
      for p in last_name_results:
        d.add(p.key().name())
      first_name_results, last_name_recur  = self.nameSearch('first_name',names[0],year,major, 1000, 0)
      i = 0
      for p in first_name_results:
        if p.key().name() in d:
          l.append(Person.buildMap(p))
          i += 1
          if i > 20:
            break
      l = sorted(l, key=lambda person: person['name'])
    
    if quick_person:
      newL = []
      for i in l:
        if 'rcsid' in i and i['rcsid'] == quick_person.key().name():
          continue
        newL.append(i)
      l = newL
      l.insert(0,Person.buildMap(quick_person))
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