#App Engine Models

from google.appengine.ext import db

class Person(db.Model):
  """Models a person in the RPI directory."""
    'Class:'           : 'class',
    'Curriculum:'      : 'major',
    'Title:'           : 'title',
    'Telephone:'       : 'phone',
    'Fax:'             : 'fax',
    'Office Location:' : 'office location',
    'Campus Mailstop:' : 'campus mailstop',
    'Mailing Address:' : 'mailing address'
  year = db.StringProperty()
  major = db.StringProperty()
  title = db.StringProperty()
  phone = db.StringProperty()
  fax = db.StringProperty()
  office_location = db.StringProperty()
  campus_mailstop = db.StringProperty()
  mailing_address = db.StringProperty()