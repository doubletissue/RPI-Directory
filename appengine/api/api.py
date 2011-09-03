from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
import cgi
import urllib
from models import Person
from django.utils import simplejson as json

class Api(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year  = urllib.unquote( cgi.escape(self.request.get('year' )) )
    major = urllib.unquote( cgi.escape(self.request.get('major')) )
    name  = urllib.unquote( cgi.escape(self.request.get('name' )) )
    
    query = Person.all()
    
    if year is not "":
      query = query.filter('year = ',year)
    if major is not "":
      query = query.filter('major = ',major)
    
    names = name.split()[:3]
    if len(names) > 0:
      query = query.filter('first_name = ', names[0])
    if len(names) > 1:
      query = query.filter('last_name = ', names[-1])
    if len(names) > 2:
      query = query.filter('middle_name = ', names[1])
    
    people = query.fetch(100)
    
    if len(names) == 1:
      query = Person.all()
      if year is not "":
        query = query.filter('year = ',year)
      if major is not "":
        query = query.filter('major = ',major)
      query = query.filter('last_name = ', names[0])
      people.extend(query.fetch(100))
    
    l = []
    
    for p in people:
      l.append(Person.buildMap(p))
    s = json.dumps(l)
    self.response.out.write(s)

class ChristiansStupidApi(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year  = urllib.unquote( cgi.escape(self.request.get('year' )) )
    major = urllib.unquote( cgi.escape(self.request.get('major')) )
    name  = urllib.unquote( cgi.escape(self.request.get('name' )) )
    
    query = Person.all()
    
    if year is not "":
      query = query.filter('year = ',year)
    if major is not "":
      query = query.filter('major = ',major)
    
    names = name.split()[:3]
    if len(names) > 0:
      query = query.filter('first_name = ', names[0])
    if len(names) > 1:
      query = query.filter('last_name = ', names[-1])
    if len(names) > 2:
      query = query.filter('middle_name = ', names[1])
    
    people = query.fetch(100)
    
    if len(names) == 1:
      query = Person.all()
      if year is not "":
        query = query.filter('year = ',year)
      if major is not "":
        query = query.filter('major = ',major)
      query = query.filter('last_name = ', names[0])
      people.extend(query.fetch(100))
    
    l = []
    
    keys = set()
    for p in people:
      m = Person.buildMap(p)
      for k in m.keys():
        keys.add(k)
    
    
    for p in people:
      m = Person.buildMap(p)
      for key in keys:
        if key not in m.keys():
          m[key] = ""
      l.append(m)
    
    d2 = {}
    d2['iTotalRecords'] = len(l)
    d2['iTotalDisplayRecords'] = len(l)
    d2['sColumns'] = 'name,email,class,major,title,phone,fax,homepage,office_location,campus_mailstop,mailing_address'
    d2['sEcho'] = urllib.unquote( cgi.escape(self.request.get('sEcho' )) )
    d2['aaData'] = l
    
    s = json.dumps(d2)
    self.response.out.write(s)
    

application = webapp.WSGIApplication(
  [
    ("/api", Api),
    ("/tableApi", ChristiansStupidApi)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()