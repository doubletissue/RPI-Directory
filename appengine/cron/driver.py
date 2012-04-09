from cron.crawler import Crawler
from models import SearchPosition
from models import Person
#from models import DepartmentKeyword

import cgi
import datetime
import urllib
import wsgiref.handlers
import logging
import string

from google.appengine.ext import db
from google.appengine.api import rdbms
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app

_INSTANCE_NAME = "christianjohnson.org:rpidirectory:christianjohnson"

NUM_THREADS = 100

#Creates a person and stores it
def putResult(d):
  """
  person = Person.buildPerson(d)
  #if person.department:
    #DepartmentKeyword.buildKeywords(person.department)
  person.put()
  """
  
  person = Person.buildPerson(d)
    
  conn = rdbms.connect(instance=_INSTANCE_NAME, database="rpidirectory")
  cursor = conn.cursor()
  query = 'REPLACE INTO rpidirectory (`name`, `campus_mailstop`, `department`, `email`, `fax`, `first_name`, `homepage`, `last_name`, `mailing_address`, `major`, `office_location`, `phone`, `rcsid`, `title`, `year`, `directory_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
  args = (person.rcsid, person.campus_mailstop, person.department, person.email, person.fax, person.first_name, person.homepage, person.last_name, person.mailing_address, person.major, person.office_location, person.phone, person.rcsid, person.title, person.year, str(person.directory_id))
  logging.info(query)
  logging.info(repr(args))
  cursor.execute(query, args)
  conn.close()

def crawlPerson(index):
  logging.info("In CrawlPerson")
  result = Crawler().getMap(index)
  
  if 'error' in result.keys():
    logging.warn("error at index" + str(index) + ", error is " + result['error'])
    if result['error'] == 'page_not_found':
      logging.warn("Invalid index: " + str(index))
      raise Exception()
    if result['error'] == 'end of database':
      logging.warn("Index out of range: " + str(index))
      memcache.set("index", 1, 86400)
      SearchPosition(key_name="index", position=1).put()
  else:
    logging.info("putting results")
    putResult(result)
  
  #if int(index) > 15000:
    #logging.info("At end of database, reseting " + str(index))
    #memcache.set("index", 1, 86400)
    #SearchPosition(key_name="index", position=1).put()

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
  
    #Spawn tasks
    for i in range(index, index + NUM_THREADS):
      taskqueue.add(url='/crawl/worker', params={'index': i}) #, target='backend'
      #Update Memcache
      if not memcache.incr("index"):
        logging.error("Memcache set failed")
    #crawlPerson(index)
      
    
    #Update Datastore
    index_from_ds = SearchPosition.get_by_key_name("index")
    if index_from_ds:
      index_from_ds.position = (index + NUM_THREADS)
    else:
      index_from_ds = SearchPosition(key_name="index", position=index)
    index_from_ds.put()

class DriverWorker(webapp.RequestHandler):
  def post(self):
    logging.info("In DriverWorker")
    index = cgi.escape(self.request.get('index'))
    crawlPerson(index)
    
  def get(self):
    logging.info("In DriverWorker")
    index = cgi.escape(self.request.get('index'))
    crawlPerson(index)
	
class FixBroken(webapp.RequestHandler):
  def get(self):
    logging.info("Fixing Broken Ones...")
    conn = rdbms.connect(instance=_INSTANCE_NAME, database="rpidirectory")
    cursor = conn.cursor()
    query = 'SELECT directory_id from rpidirectory where first_name LIKE "%>%"'
    cursor.execute(query)
    logging.info("Found " + str(cursor.rowcount) + " broken entries")
    if cursor.rowcount > 0:
      for row in cursor.fetchall():
        taskqueue.add(url='/crawl/worker', params={'index': str(row[0])}) 
    conn.close()
    
	
application = webapp.WSGIApplication([
  ("/crawl/main", Driver),
  ("/crawl/worker", DriverWorker),
  ("/crawl/fix", FixBroken)])

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()