from cron.crawler import Crawler
from models import SearchPosition
from models import Person
from models import DepartmentKeyword

import cgi
import datetime
import urllib
import wsgiref.handlers
import logging
import string

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app


NUM_THREADS = 100

#Creates a person and stores it
def putResult(d):
  person = Person.buildPerson(d)
  if person.department:
    DepartmentKeyword.buildKeywords(person.department)
  person.put()

class Driver(webapp.RequestHandler):
  def get(self):
    index = memcache.get("index")

    if not index:
      index_from_ds = SearchPosition.get_by_key_name("index")
      if not index_from_ds:
        index = 1
        #Add it to datastore
        SearchPosition(key_name="index", position=index).put()
      else:
        index = index_from_ds.position
      memcache.add("index", index, 86400)

    #Spawn 5 tasks and do them
    for i in range(index, index + NUM_THREADS):
      taskqueue.add(url='/crawl/worker', params={'index': i}, target='backend')

      #Update Memcache
      if not memcache.incr("index"):
        logging.error("Memcache set failed")
    
    #Update DataStore
    index_from_ds = SearchPosition.get_by_key_name("index")
    if index_from_ds:
      index_from_ds.position = (index + NUM_THREADS)
    else:
      index_from_ds = SearchPosition(key_name="index", position=index)
    index_from_ds.put()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(index)


class DriverWorker(webapp.RequestHandler):
  def get(self):
    index = cgi.escape(self.request.get('index'))
    result = Crawler().getMap(index)
    if 'error' in result.keys():
      logging.error("error at index" + index + ", error is " + result['error'])
      if result['error'] == 'page_not_found':
        logging.error("Invalid index: " + index)
        raise Exception()
      if result['error'] == 'end of database':
        logging.error("Index out of range: " + index)
        memcache.set("index", 1, 86400)
        SearchPosition(key_name="index", position=1).put()
    else:
      putResult(result)
      self.response.out.write(result)
  def post(self):
    index = cgi.escape(self.request.get('index'))
    result = Crawler().getMap(index)
    if 'error' in result.keys():
      logging.error("error at index" + index + ", error is " + result['error'])
      if result['error'] == 'page_not_found':
        logging.error("Invalid index: " + index)
        raise Exception()
      if result['error'] == 'end of database':
        logging.error("Index out of range: " + index)
        memcache.set("index", 1, 86400)
        SearchPosition(key_name="index", position=1).put()
    else:
      putResult(result)
	
application = webapp.WSGIApplication([
  ("/crawl/main", Driver),
  ("/crawl/worker", DriverWorker)])

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()