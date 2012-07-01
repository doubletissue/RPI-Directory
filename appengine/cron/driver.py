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

import string

_INDEX_NAME = 'person'

def split_words(field_name,s):
    s = string.translate(str(s),None,string.punctuation)
    l = s.replace('\n',' ').split()
    r = []
    for i in range(len(l)):
        try:
            int(l[i])
            continue
        except:
            pass
        r.append(search.TextField(name=field_name+str(i), value=l[i]))
    return r

#Creates a person and stores it
def createDocument(person):
    fields = []
    if person.first_name:
        for i in range(len(person.first_name)):
            for j in range(i+1,len(person.first_name)+1):
                fields.append(search.TextField(name='first_name'+str(i)+'to'+str(j), value=person.first_name[i:j]))
    if person.middle_name:
        fields.append(search.TextField(name='middle_name', value=person.middle_name))
    if person.last_name:
        for i in range(len(person.last_name)):
            for j in range(i+1,len(person.last_name)+1):
                fields.append(search.TextField(name='last_name'+str(i)+'to'+str(j), value=person.last_name[i:j]))
    if person.department:
        fields.extend(split_words('department',person.department))
    if person.email:
        fields.extend(split_words('email',person.email))
    if person.rcsid:
        fields.extend(split_words('rcsid',person.rcsid))
    if person.year:
        fields.extend(split_words('year',person.year))
    if person.major:
        fields.extend(split_words('major',person.major))
    if person.title:
        fields.extend(split_words('title',person.title))
    if person.phone:
        fields.extend(split_words('phone',person.phone))
    if person.fax:
        fields.extend(split_words('fax',person.fax))
    if person.homepage:
        fields.extend(split_words('homepage',person.homepage))
    if person.office_location:
        fields.extend(split_words('office_location',person.office_location))
    if person.campus_mailstop:
        fields.extend(split_words('campus_mailstop',person.campus_mailstop))
    if person.mailing_address:
        fields.extend(split_words('mailing_address',person.mailing_address))

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
