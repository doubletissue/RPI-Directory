#App Engine Models

from google.appengine.ext import db
import string

class Person(db.Model):
  """Models a person in the RPI directory."""
  first_name      = db.StringProperty()
  middle_name     = db.StringProperty()
  last_name       = db.StringProperty()
  department      = db.StringProperty()
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
  date_crawled    = db.DateTimeProperty(auto_now=True)
  directory_id    = 0
  
  @staticmethod
  def buildPerson(d):
    person = Person()
    
    if 'email' in d:
      rcsid = string.rsplit(d['email'],'@',1)[0]
      person = Person(key_name = rcsid)
      person.rcsid = rcsid
    elif 'name' in d:
      person = Person(key_name = d['name'])
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
      person.key_name = d['email']
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
      name += p.first_name.title()
    #if p.middle_name is not None:
      #name += ' ' + p.middle_name.title()
    if p.last_name is not None:
      name += ' ' + p.last_name.title()
    if name is not "":
      d['name'] = name
    
    if p.year is not None:
      d['year'] = p.year.title()
    
    if p.major is not None:
      d['major'] = p.major.title()
    
    if p.department is not None:
      d['department'] = p.department.title()
    
    if p.title is not None:
      d['title'] = p.title.title()
    
    if p.phone is not None:
      d['phone'] = p.phone.title()
    
    if p.fax is not None:
      d['fax'] = p.fax.title()
    
    if p.homepage is not None:
      d['homepage'] = p.homepage.title()
    
    if p.office_location is not None:
      d['office_location'] = p.office_location.title()
    
    if p.campus_mailstop is not None:
      d['campus_mailstop'] = p.campus_mailstop.title()
    
    if p.mailing_address is not None:
      d['mailing_address'] = p.mailing_address.title()
    
    if p.directory_id is not None:
      d['directory_id'] = p.directory_id
    
    return d
  
  

class SearchPosition(db.Model):
  """Model to store Crawler position."""
  position = db.IntegerProperty()

#class DepartmentKeyword(db.Model):
  #"""Model to store a single work from a major, for searching purposes"""
  #departments = db.ListProperty
  
  #@staticmethod
  #def buildKeywords(s):
    #for word in s.split():
      #d = DepartmentKeyword.get_by_key_name(word)
      #if not d:
        #w = DepartmentKeyword(key_name = word)
        #w.department = [s]
        #w.put()
      #elif s not in d.departments:
        #d.departments.append(s)
        #d.put()