#App Engine Models

from google.appengine.api import users
from google.appengine.ext import ndb
import string
import random
import sys
from datetime import datetime

class Person(ndb.Model):
  """Models a person in the RPI directory."""
  first_name = ndb.StringProperty()
  middle_name = ndb.StringProperty()
  last_name = ndb.StringProperty()
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
  directory_id = ndb.IntegerProperty()
  date_emailed = ndb.DateTimeProperty()
  mailing_address_html = ndb.ComputedProperty(lambda self: self.mailing_address.replace('\n', '<br />') if self.mailing_address else None)
  picture = ndb.BlobProperty()
  linked_account = ndb.UserProperty()
  email_html = ndb.ComputedProperty(lambda self: self.email.replace('@', ' [at] ').replace('.', ' [dot] ') if self.email else None)
  
  @staticmethod
  def buildPerson(d):
    person = Person()

    if 'email' in d:
      rcsid = string.rsplit(d['email'],'@', 1)[0]
      person = Person(id = rcsid)
      person.rcsid = rcsid
    elif 'name' in d:
      person = Person(id = d['name'])
      person.rcsid = d['name']
    else:
      # No name for the person, no point in making them
      person = Person()
      return person
    
    if 'name' in d:
      names = d['name'].split()[:3]
      if len(names) > 0:
        person.first_name = names[0]
      if len(names) > 1:
        person.last_name = names[-1]
      #if len(names) > 2:
        #person.middle_name = names[1]
    if 'email' in d:
      person.email = d['email']
      person.id = d['email']
    if 'year' in d:
      person.year = d['year']
    if 'major' in d:
      person.major = d['major']
    if 'department' in d:
      person.department = d['department']
    if 'title' in d:
      person.title = d['title']
    if 'phone' in d:
      person.phone = d['phone']
    if 'fax' in d:
      person.fax = d['fax']
    if 'homepage' in d:
      person.homepage = d['homepage']
    if 'office_location' in d:
      person.office_location = d['office_location']
    if 'campus_mailstop' in d:
      person.campus_mailstop = d['campus_mailstop']
    if 'mailing_address' in d:
      person.mailing_address = d['mailing_address']
    if 'directory_id' in d:
      person.directory_id = d['directory_id']
    person.date_emailed = datetime.min
    
    return person
  
  @staticmethod
  def buildMap(p):
    
    d = {}
    
    if p.email is not None:
      d['email'] = str(p.email)
    if p.email_html is not None:
      d['email_html'] = str(p.email_html)
    if p.rcsid is not None:
      d['rcsid'] = str(p.rcsid)
    
    name = ''
    if p.first_name is not None:
      name += str(p.first_name.title())
    #if p.middle_name is not None:
      #name += ' ' + p.middle_name.title()
    if p.last_name is not None:
      name += ' ' + str(p.last_name.title())
    if name is not "":
      d['name'] = str(name)
    
    if p.year is not None:
      d['year'] = str(p.year.title())
    
    if p.major is not None:
      d['major'] = str(p.major.title())
    
    if p.department is not None:
      d['department'] = str(p.department.title())
    
    if p.title is not None:
      d['title'] = str(p.title.title())
    
    if p.phone is not None:
      d['phone'] = str(p.phone.title())
    
    if p.fax is not None:
      d['fax'] = str(p.fax.title())
    
    if p.homepage is not None:
      d['homepage'] = str(p.homepage.title())
    
    if p.office_location is not None:
      d['office_location'] = str(p.office_location.title())
    
    if p.campus_mailstop is not None:
      d['campus_mailstop'] = str(p.campus_mailstop.title())
    
    if p.mailing_address is not None:
      d['mailing_address'] = str(p.mailing_address.title())
    
    if p.directory_id is not None:
      d['directory_id'] = str(p.directory_id)
    
    return d
  

class SearchPosition(ndb.Model):
  """Model to store Crawler position."""
  position = ndb.IntegerProperty()