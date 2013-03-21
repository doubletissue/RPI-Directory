import webapp2
from google.appengine.api import users
import os
import jinja2
import logging
from models import Person
from models import StatsObject
import hashlib
import urllib
import gviz_api

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

CHART_HEIGHT = 500
CHOP = 30

class Stats(webapp2.RequestHandler):
  def get(self):
    
    #Site is under maintaince
    #template = jinja_environment.get_template('html/index.html')
    template = jinja_environment.get_template('html/maintenance.html')
    self.response.out.write(template.render({}))
    exit(0)
    
    #num_people = Person.query().count(limit=15000)
    #num_stats = StatsObject.query().count()
    
    majors = StatsObject.get_by_id('global:major').json
    first_name = StatsObject.get_by_id('global:first_name').json
    last_name = StatsObject.get_by_id('global:last_name').json
    year = StatsObject.get_by_id('global:year').json
    dept = StatsObject.get_by_id('global:department').json
    title = StatsObject.get_by_id('global:title').json
    type_person = StatsObject.get_by_id('global:type').json
    
    majors = sorted(majors.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    first_name = sorted(first_name.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    last_name = sorted(last_name.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    year = sorted(year.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    dept = sorted(dept.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    title = sorted(title.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    type_person = sorted(type_person.items(), key=lambda x: x[1], reverse=True)[:CHOP]
    
    stats = [{'title': 'Major', 'data': majors},
             {'title': 'Year', 'data': year},
             {'title': 'First Name', 'data': first_name},
             {'title': 'Last Name', 'data': last_name},
             {'title': 'Title', 'data': title},
             {'title': 'Department', 'data': dept},
             {'title': 'Position', 'data': type_person}]
    
    template_values = {'active': 'insights',
                       #'num_people': num_people,
                       #'num_stats': num_stats,
                       'stats': stats,
                       'chart_height': CHART_HEIGHT}
    template = jinja_environment.get_template('html/insights.html')
    self.response.out.write(template.render(template_values))
    
class ChartsAPI(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    name = self.request.get('name', 'michael').split()[0].lower()
    chart_type = self.request.get('type', 'major')
    tqx = self.request.get('tqx', '')
    req_id = tqx[6:]
    if chart_type == 'major':
      description = {("major", "string", "Major"): ("amount", "number", "Amount")}
    else:
      description = {("year", "string", "Year"): ("amount", "number", "Amount")}
    data = StatsObject.get_by_id(name)
    try:
      if chart_type == 'major':
        data = data.json['first_name']['major']
      else:
        data = data.json['first_name']['year']
    except Exception as e:
      data = {}
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)
    self.response.out.write(data_table.ToJSonResponse(order_by="amount", req_id=req_id))

app = webapp2.WSGIApplication([('/insights', Stats), ('/insights_chart.*', ChartsAPI)])