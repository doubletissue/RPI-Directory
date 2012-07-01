from cron.crawler import Crawler
from models import SearchPosition
from models import Person

import cgi
import logging

from google.appengine.ext import webapp
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import search

_INSTANCE_NAME = "christianjohnson.org:rpidirectory:christianjohnson"

NUM_THREADS = 100

_INDEX_NAME = 'person'

#Creates a person and stores it
def createDocument(person):
    fields = []
    if person.first_name:
        fields.append(search.TextField(name='first_name', value=person.first_name))
    if person.middle_name:
        fields.append(search.TextField(name='middle_name', value=person.middle_name))
    if person.last_name:
        fields.append(search.TextField(name='last_name', value=person.last_name))
    if person.department:
        fields.append(search.TextField(name='department', value=person.department))
    if person.email:
        fields.append(search.TextField(name='email', value=person.email))
    if person.rcsid:
        fields.append(search.TextField(name='rcsid', value=person.rcsid))
    if person.year:
        fields.append(search.TextField(name='year', value=person.year))
    if person.major:
        fields.append(search.TextField(name='major', value=person.major))
    if person.title:
        fields.append(search.TextField(name='title', value=person.title))
    if person.phone:
        fields.append(search.TextField(name='phone', value=person.phone))
    if person.fax:
        fields.append(search.TextField(name='fax', value=person.fax))
    if person.homepage:
        fields.append(search.TextField(name='homepage', value=person.homepage))
    if person.office_location:
        fields.append(search.TextField(name='office_location', value=person.office_location))
    if person.campus_mailstop:
        fields.append(search.TextField(name='campus_mailstop', value=person.campus_mailstop))
    if person.mailing_address:
        fields.append(search.TextField(name='mailing_address', value=person.mailing_address))
    if person.date_crawled:
        fields.append(search.DateField(name='date_crawled', value=person.date_crawled.date()))
    if person.directory_id:
        fields.append(search.NumberField(name='directory_id', value=person.directory_id))

    return search.Document(doc_id=person.rcsid or None, fields=fields)

def putResult(d):
  person = Person.buildPerson(d)
  #if person.department:
    #DepartmentKeyword.buildKeywords(person.department)
  person.put()
  search.Index(name=_INDEX_NAME).add(createDocument(person))


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
      SearchPosition(id="index", position=1).put()
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
      index_from_ds = SearchPosition.get_by_id("index")
      if not index_from_ds:
        index = 1
        #Add it to datastore
        SearchPosition(id="index", position=index).put()
      else:
        index = index_from_ds.position
      memcache.add("index", index, 86400)

    #Spawn tasks
    for i in range(index, index + NUM_THREADS):
      taskqueue.add(url='/crawl/worker', params={'index': i}) #, target='backend'
      #Update Memcache
      if not memcache.incr("index"):
        logging.error("Memcache set failed")

    #Update Datastore
    index_from_ds = SearchPosition.get_by_id("index")
    if index_from_ds:
      index_from_ds.position = (index + NUM_THREADS)
    else:
      index_from_ds = SearchPosition(id="index", position=index)
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

application = webapp.WSGIApplication([
  ("/crawl/main", Driver),
  ("/crawl/worker", DriverWorker),
  ("/crawl/fix", FixBroken)])

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
