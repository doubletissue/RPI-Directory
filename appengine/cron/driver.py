from cron.crawler import Crawler
from models import SearchPosition
from models import Person

from cron.mutex import Mutex

import cgi
import logging
import webapp2

from google.appengine.api import taskqueue
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import search

_INSTANCE_NAME = "christianjohnson.org:rpidirectory:christianjohnson"

NUM_THREADS = 200

import string

_INDEX_NAME = 'person'

def split_words(field_name, s):
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

#Creates a person and stores it
def createDocument(person):
    fields = []
    if person.first_name:
        for i in range(len(person.first_name)):
            for j in range(i + 1, len(person.first_name) + 1):
                fields.append(search.TextField(name='first_name' + str(i) + 'to' + str(j), value=str(person.first_name[i:j])))
    if person.middle_name:
        fields.append(search.TextField(name='middle_name', value=str(person.middle_name)))
    if person.last_name:
        for i in range(len(person.last_name)):
            for j in range(i + 1, len(person.last_name) + 1):
                fields.append(search.TextField(name='last_name' + str(i) + 'to' + str(j), value=str(person.last_name[i:j])))
    if person.department:
        fields.extend(split_words('department', person.department))
    if person.email:
        fields.extend(split_words('email', person.email))
    if person.rcsid:
        fields.extend(split_words('rcsid', person.rcsid))
    if person.year:
        fields.extend(split_words('year', person.year))
    if person.major:
        fields.extend(split_words('major', person.major))
    if person.title:
        fields.extend(split_words('title', person.title))
    if person.phone:
        fields.extend(split_words('phone', person.phone))
    if person.fax:
        fields.extend(split_words('fax', person.fax))
    if person.homepage:
        fields.extend(split_words('homepage', person.homepage))
    if person.office_location:
        fields.extend(split_words('office_location', person.office_location))
    if person.campus_mailstop:
        fields.extend(split_words('campus_mailstop', person.campus_mailstop))
    if person.mailing_address:
        fields.extend(split_words('mailing_address', person.mailing_address))

    return search.Document(doc_id=str(person.rcsid.split()[0]) or str(person.first_name + ' ' + person.last_name), fields=fields)

def putResult(d):
  person = Person.buildPerson(d)
  #if person.department:
    #DepartmentKeyword.buildKeywords(person.department)
  person.put()
  search.Index(name=_INDEX_NAME).add(createDocument(person))


def crawlPerson(index):
    logging.info("In CrawlPerson")
    
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
    index = cgi.escape(self.request.get('index'))
    crawlPerson(index)

  def get(self):
    logging.info("In DriverWorker")
    index = cgi.escape(self.request.get('index'))
    crawlPerson(index)

app = webapp2.WSGIApplication([
  ("/crawl/main", Driver),
  ("/crawl/worker", DriverWorker)])
