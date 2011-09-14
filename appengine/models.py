#App Engine Models

from google.appengine.ext import db
import string

class Person(db.Model):
  """Models a person in the RPI directory."""
  first_name      = db.StringProperty()
  middle_name     = db.StringProperty()
  last_name       = db.StringProperty()
  email           = db.StringProperty()
  rcsid           = db.StringProperty()
  year            = db.StringProperty()
  major           = db.StringProperty()
  title           = db.StringProperty()
  phone           = db.StringProperty()
  fax             = db.StringProperty()
  homepage        = db.StringProperty()
  office_location = db.StringProperty(multiline=True)
  campus_mailstop = db.StringProperty(multiline=True)
  mailing_address = db.StringProperty(multiline=True)
  
  @staticmethod
  def buildPerson(d):
    person = Person()
    
    if 'email' in d:
      rcsid = string.rsplit(d['email'],'@',1)[0]
      person = Person(key_name = rcsid)
      person.rcsid = rcsid
    
    if 'name' in d:
      names = d['name'].split()[:3]
      if len(names) > 0:
        person.first_name = names[0]
      if len(names) > 1:
        person.last_name = names[-1]
      if len(names) > 2:
        person.middle_name = names[1]
    if 'email' in d:
      person.email = d['email']
      person.key_name = d['email']
    if 'class' in d:
      person.year = d['class']
    if 'major' in d:
      person.major = d['major']
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
    
    return person
  
  @staticmethod
  def buildMap(p):
    
    d = {}
    
    if p.email is not None:
      d['email'] = p.email
    if p.rcsid is not None:
      d['rcsid'] = p.rcsid
    
    name = ''
    if p.first_name is not None:
      name += p.first_name
    if p.middle_name is not None:
      name += ' ' + p.middle_name
    if p.last_name is not None:
      name += ' ' + p.last_name
    if name is not "":
      d['name'] = name
    
    if p.year is not None:
      d['class'] = p.year
    
    if p.major is not None:
      d['major'] = p.major
    
    if p.title is not None:
      d['title'] = p.title
    
    if p.phone is not None:
      d['phone'] = p.phone
    
    if p.fax is not None:
      d['fax'] = p.fax
    
    if p.homepage is not None:
      d['homepage'] = p.homepage
    
    if p.office_location is not None:
      d['office_location'] = p.office_location
    
    if p.campus_mailstop is not None:
      d['campus_mailstop'] = p.campus_mailstop
    
    if p.mailing_address is not None:
      d['mailing_address'] = p.mailing_address
    
    return d
  
  

class SearchPosition(db.Model):
  """Model to store Crawler position."""
  position = db.IntegerProperty()