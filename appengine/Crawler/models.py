#App Engine Models

from google.appengine.ext import db

class Person(db.Model):
  """Models a person in the RPI directory."""
  year = db.StringProperty()
  major = db.StringProperty()
  title = db.StringProperty()
  phone = db.StringProperty()
  fax = db.StringProperty()
  office_location = db.StringProperty()
  campus_mailstop = db.StringProperty()
  mailing_address = db.StringProperty()

class SearchPosition(db.Model):
	"""Model to store Crawler position."""
	position = db.IntegerProperty()