from cron.crawler import Crawler
from models import SearchPosition
from models import Person

from cron.mutex import Mutex

import cgi
import logging
import webapp2
import urllib

from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import search

NUM_THREADS = 500

import string

_INDEX_NAME = 'person'

def split_words(field_name, s):
    if not s:
      return []
    field_name = str(field_name)
    s = str(s)
    for c in string.punctuation:
        s = s.replace(c, '')
    l = s.replace('\n', ' ').split()
    r = []
    for i in range(len(l)):
        try:
            int(l[i])
            continue
        except:
            pass
        r.append(search.TextField(name=field_name + str(i), value=l[i]))
    return r
    
def makeFullIndex(field_name,s):
  if not s:
    return []
  field_name = str(field_name)
  s = str(s)
  for c in string.punctuation:
    s = s.replace(c, '')
  r = []
  
  s = s.split(' ')
  for w in s:
      for i in range(len(w)):
          for j in range(i + 1, len(w) + 1):
              r.append(search.TextField(name=field_name + str(i) + 'to' + str(j), value=str(w[i:j])))
          
  return r
    
searchableAttributes = [
  'department',
  'email',
  'rcsid',
  'year',
  'major',
  'title',
  'phone',
  'fax',
  'homepage',
  'office_location',
  'campus_mailstop',
  'mailing_address'
]

fullSearchAttributes = [
  'first_name',
  'middle_name',
  'prefered_name',
  'last_name'
]

#Creates a person and stores it
def createDocument(person):
    fields = []
    
    for attr in fullSearchAttributes:
      fields.extend(makeFullIndex(attr, getattr(person,attr,'')))
                
    for attr in searchableAttributes:
      fields.extend(split_words(attr, getattr(person,attr,'')))

    return search.Document(doc_id=person.rcsid, fields=fields)

def putResult(d):
  if 'rcsid' not in d:
    return
  key = d['rcsid']
  prev_person = Person.get_by_id(key)
  if prev_person:
    logging.info("Updating %s", key)
    prev_person.update(d)
    prev_person.put()
    search.Index(name=_INDEX_NAME).add(createDocument(prev_person))
  else:
    logging.info("New %s", key)
    person = Person.buildPerson(d)
    person.put()
    search.Index(name=_INDEX_NAME).add(createDocument(person))


def crawlPerson(index):
    logging.info("In CrawlPerson")

    if index:    
      result = Crawler().getMap(index)
      logging.info(str(result))
      putResult(result)
      return
    
    mutex = Mutex('mutex lock')
    try:
        mutex.lock()
        index_from_ds = SearchPosition.get_by_id("index")
        if index_from_ds:
            index = index_from_ds.position
        else:
            index_from_ds = SearchPosition(id='index',position=1)
            index_from_ds.put()
            index = 1
            
        result = Crawler().getMap(index)
        logging.info(str(result))
        
        if 'error' in result.keys():
            logging.warn("error at index" + str(index) + ", error is " + result['error'])
            if result['error'] == 'page_not_found':
                logging.warn("Invalid index: " + str(index))
                raise Exception()
            if result['error'] == 'end of database':
                logging.warn("Index out of range: " + str(index))
                index_from_ds.position = 1
                index_from_ds.put()
        else:
            logging.info("putting results")
    
            putResult(result)
    
            index_from_ds.position = (int(index) + 1)
            logging.info("INCREMENT " + str(index))
            index_from_ds.put()
            mutex.unlock()
    except Exception as e:
        raise e
    finally:
        mutex.unlock()

class Driver(webapp2.RequestHandler):
    def get(self):
        for i in range(NUM_THREADS):
            taskqueue.add(url='/crawl/worker') #, target='backend'
    
class DriverWorker(webapp2.RequestHandler):
  def post(self):
    logging.info("In DriverWorker")
    index = cgi.escape(self.request.get('key'))
    crawlPerson(index)

  def get(self):
    logging.info("In DriverWorker")
    index = cgi.escape(self.request.get('key'))
    crawlPerson(index)

app = webapp2.WSGIApplication([
  ("/crawl/main", Driver),
  ("/crawl/worker", DriverWorker)])
