#App Engine Models

from google.appengine.api import users
from google.appengine.ext import ndb
import string
import random
import sys
from datetime import datetime

person_attributes = [
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

map_attributes = [
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
  'directory_id',
  'mailing_address_html',
  'email_html',
  'name'
]

def generateName(strings):
  s = ''
  for st in strings:
    if st:
      s += st + ' '
  s = s[:-1]
  return s

class Person(ndb.Model):
  """Models a person in the RPI directory."""
  first_name = ndb.StringProperty()
  middle_name = ndb.StringProperty()
  last_name = ndb.StringProperty()
  name = ndb.ComputedProperty(lambda self: generateName([self.first_name,self.middle_name,self.last_name]))
  department = ndb.StringProperty()
  email = ndb.StringProperty()
  rcsid = ndb.StringProperty()
  year = ndb.StringProperty()
  major = ndb.StringProperty()
  title = ndb.StringProperty()
  phone = ndb.StringProperty()
  fax = ndb.StringProperty()
  homepage = ndb.StringProperty()
  office_location = ndb.StringProperty()
  campus_mailstop = ndb.StringProperty()
  mailing_address = ndb.StringProperty()
  date_crawled = ndb.DateTimeProperty(auto_now=True)
  directory_id = ndb.StringProperty()
  mailing_address_html = ndb.ComputedProperty(lambda self: self.mailing_address.replace('\n', '<br />') if self.mailing_address else None)
  picture = ndb.BlobProperty()
  linked_account = ndb.UserProperty()
  email_html = ndb.ComputedProperty(lambda self: self.email.replace('@', ' [at] ').replace('.', ' [dot] ') if self.email else None)
  
  def update(self, d):
    for attr in person_attributes:
      v = d.get(attr,None)
      if v:
        if type(v) == type('string'):
          v = v.lower()
        setattr(self,attr,v)
  
  @staticmethod
  def buildPerson(d):
    
    if 'rcsid' not in d:
      return None
    
    person = Person(id = d['rcsid'])
    
    for attr in person_attributes:
      v = d.get(attr,None)
      if v:
        if type(v) == type('string'):
          v = v.lower()
        setattr(person,attr,v)
    
    return person
  
  @staticmethod
  def buildMap(p):
    
    d = {}
    
    for attr in map_attributes:
      v = getattr(p,attr,None)
      if v:
        if type(v) == type('string'):
          v = v.lower()
        d[attr] = v
    
    return d
  

class SearchPosition(ndb.Model):
  """Model to store Crawler position."""
  position = ndb.IntegerProperty()
      
class StatsObject(ndb.Model):
    count = ndb.IntegerProperty()
    stat_type = ndb.StringProperty
    name = ndb.StringProperty