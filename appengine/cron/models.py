#App Engine Models

from google.appengine.ext import db

class Person(db.Model):
  """Models a person in the RPI directory."""
  first_name = db.StringProperty()
  middle_name = db.StringProperty()
  last_name = db.StringProperty()
  email = db.StringProperty()
  year = db.StringProperty()
  major = db.StringProperty()
  title = db.StringProperty()
  phone = db.StringProperty()
  fax = db.StringProperty()
  homepage = db.StringProperty()
  office_location = db.StringProperty(multiline=True)
  campus_mailstop = db.StringProperty(multiline=True)
  mailing_address = db.StringProperty(multiline=True)

class SearchPosition(db.Model):
  """Model to store Crawler position."""
  position = db.IntegerProperty()