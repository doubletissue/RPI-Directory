#App Engine Models

from google.appengine.api import users
from google.appengine.ext import ndb
import string
import random
import sys
from datetime import datetime

attributes = [
  'email',
  'first_name',
  'middle_name',
  'last_name',
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
  'mailing_address',
  'directory_id'
]

class Person(ndb.Model):
  """Models a person in the RPI directory."""
  first_name = ndb.StringProperty(default='')
  middle_name = ndb.StringProperty(default='')
  last_name = ndb.StringProperty(default='')
  name = ndb.ComputedProperty(lambda self: string.join([self.first_name,self.middle_name,self.last_name],' '))
  department = ndb.StringProperty(default='')
  email = ndb.StringProperty(default='')
  rcsid = ndb.StringProperty(default='')
  year = ndb.StringProperty(default='')
  major = ndb.StringProperty(default='')
  title = ndb.StringProperty(default='')
  phone = ndb.StringProperty(default='')
  fax = ndb.StringProperty(default='')
  homepage = ndb.StringProperty(default='')
  office_location = ndb.StringProperty(default='')
  campus_mailstop = ndb.StringProperty(default='')
  mailing_address = ndb.StringProperty(default='')
  date_crawled = ndb.DateTimeProperty(auto_now=True)
  directory_id = ndb.StringProperty(default='')
  date_emailed = ndb.DateTimeProperty()
  mailing_address_html = ndb.ComputedProperty(lambda self: self.mailing_address.replace('\n', '<br />') if self.mailing_address else None)
  picture = ndb.BlobProperty()
  linked_account = ndb.UserProperty()
  email_html = ndb.ComputedProperty(lambda self: self.email.replace('@', ' [at] ').replace('.', ' [dot] ') if self.email else None)
  
  @staticmethod
  def buildPerson(d):
    
    if 'rcsid' not in d:
      return None
    
    person = Person(id = d['rcsid'])
    
    for attr in attributes:
      setattr(person,attr,d.get(attr,'').lower())
      
    person.date_emailed = datetime.min
    
    return person
  
  @staticmethod
  def buildMap(p):
    
    d = {}
    
    for attr in attributes:
      d[attr] = getattr(p,attr).lower()
      
    d['name'] = p.name
    
    return d
  

class SearchPosition(ndb.Model):
  """Model to store Crawler position."""
  position = ndb.IntegerProperty()
      
class StatsObject(ndb.Model):
    count = ndb.IntegerProperty()
    stat_type = ndb.StringProperty
    name = ndb.StringProperty