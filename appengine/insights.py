import webapp2
from google.appengine.api import users
import os
import jinja2
import logging
from models import Person
from models import StatsObject
import hashlib
import urllib

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Stats(webapp2.RequestHandler):
  def get(self):
    number_claimed = Person.query(Person.linked_account != None).count()
    unclaimed = Person.query().count(limit=15000) - number_claimed
    
    majors = StatsObject.get_by_id('major').json
    first_name = StatsObject.get_by_id('first_name').json
    last_name = StatsObject.get_by_id('last_name').json
    year = StatsObject.get_by_id('year').json
    del year['year']
    dept = StatsObject.get_by_id('department').json
    
    stats = [{'title': 'Major', 'data': majors},
             {'title': 'Year', 'data': year},
             {'title': 'First Name', 'data': first_name}]
    
    logging.info(majors)
    
    template_values = {'active': 'stats',
                       'number_claimed': number_claimed,
                       'unclaimed': unclaimed,
                       'stats': stats}
    template = jinja_environment.get_template('html/insights.html')
    self.response.out.write(template.render(template_values))
    

app = webapp2.WSGIApplication([('/insights.*', Stats)])