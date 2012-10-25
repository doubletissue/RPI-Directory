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
  'prefered_name',
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
  'prefered_name',
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
  'name',
  'type'
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
  first_name = ndb.StringProperty(indexed=False)
  prefered_name = ndb.StringProperty(indexed=False)
  middle_name = ndb.StringProperty(indexed=False)
  last_name = ndb.StringProperty(indexed=False)
  name = ndb.ComputedProperty(lambda self: generateName([self.first_name, self.middle_name, self.last_name]))
  department = ndb.StringProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)
  rcsid = ndb.StringProperty()
  year = ndb.StringProperty(indexed=False)
  major = ndb.StringProperty(indexed=False)
  title = ndb.StringProperty(indexed=False)
  phone = ndb.StringProperty(indexed=False)
  fax = ndb.StringProperty(indexed=False)
  homepage = ndb.StringProperty(indexed=False)
  office_location = ndb.StringProperty(indexed=False)
  campus_mailstop = ndb.StringProperty(indexed=False)
  mailing_address = ndb.StringProperty(indexed=False)
  date_crawled = ndb.DateTimeProperty(auto_now=True,indexed=False)
  directory_id = ndb.StringProperty(indexed=False)
  mailing_address_html = ndb.ComputedProperty(lambda self: self.mailing_address.replace('\n', '<br />') if self.mailing_address else None)
  picture = ndb.BlobProperty()
  linked_account = ndb.UserProperty()
  email_html = ndb.ComputedProperty(lambda self: self.email.replace('@', ' [at] ').replace('.', ' [dot] ') if self.email else None)
  type = ndb.ComputedProperty(lambda self: 'student' if self.major else ('faculty' if self.department else 'other'))
  
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
    name = ndb.StringProperty(indexed=False)
    json = ndb.JsonProperty(indexed=False)
    
class SuggestObject(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    json = ndb.JsonProperty(indexed=False)
