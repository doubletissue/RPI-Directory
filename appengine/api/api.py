import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.api import mail
import logging
import cgi
import urllib
from models import Person
import json
import string

from google.appengine.api import search

_INDEX_NAME = 'person-db2'
_PAGE_SIZE = 20

row_attributes = (['first_name',
                   'last_name',
                   'campus_mailstop',
                   'department',
                   'email',
                   'fax',
                   'homepage',
                   'mailing_address',
                   'major',
                   'office_location',
                   'phone',
                   'rcsid',
                   'title',
                   'year'])


query_attributes = (['first_name',
                     'last_name',
                     'campus_mailstop',
                     'department',
                     'mailing_address',
                     'major',
                     'office_location',
                     'rcsid',
                     'title',
                     'year'])

def CamelCase(s):
  if s == "":
    return ""

  ss = s.split(" ")
  for i in range(len(ss)):
    if len(ss[i]) in [0, 1]:
      ss[i] = ss[i].upper()
    else:
      ss[i] = ss[i][0].upper() + ss[i][1:]
  return " ".join(ss)

def parse_person_from_sql(raw_row):
  output = {}

  #Parse name specially
  n = ''
  if raw_row[0] != None:
    n += raw_row[0] + ' '
  if raw_row[1] != None:
    n += raw_row[1]
  if n is not '':
    output["name"] = cgi.escape(CamelCase(n))

  #Parse the rest
  for attribute, raw_row_data in zip(row_attributes[2:], raw_row[2:]):
    if raw_row_data not in [None, "None"]:
      if attribute in ["department", "mailing_address", "office_location", "major", "title", "year"]:
        output[attribute] = cgi.escape(CamelCase(raw_row_data))
      else:
        output[attribute] = cgi.escape(raw_row_data)

  return output

def parse_int(i, default):
  if i == '':
    return default
  else:
    return int(i)

class Api(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    search_query = str(urllib.unquote(cgi.escape(self.request.get('q')).lower()[:100]))
    name = str(urllib.unquote(cgi.escape(self.request.get('name')).lower()[:50]))
    token = str(urllib.unquote(cgi.escape(self.request.get('token'))))
    page_num = parse_int(urllib.unquote(cgi.escape(self.request.get('page_num'))), 1)
    page_size = parse_int(urllib.unquote(cgi.escape(self.request.get('page_size'))), 20)
    
    s = ''
    for c in search_query:
      if c in string.letters or c in string.digits or c == ' ':
        s += c
    search_query = s

    if search_query + name == "":
      d = {}
      d['data'] = []
      d['token'] = token
      d['q'] = ""
      s = json.dumps(d)
      self.response.out.write(s)
      return

    if search_query == "":
      search_query = name

    if page_size > _PAGE_SIZE or page_size < 1:
      page_size = _PAGE_SIZE

    queries = map(str, search_query.split())
    queries = sorted(queries)
    query_string = ' AND '.join(queries)
    
    d = {}
    d["data"] = []
    d["token"] = token
    d["q"] = search_query
    
    data = []
    #Sort results by first name descending
    expr_list = [search.SortExpression(
                expression='first_name', default_value='',
                direction=search.SortExpression.DESCENDING)]
    # construct the sort options 
    sort_opts = search.SortOptions(expressions=expr_list)
    offset_num = (page_num - 1) * page_size
    query_options = search.QueryOptions(limit=page_size, offset=offset_num, 
          ids_only=True, sort_options=sort_opts)
    results = search.Index(name=_INDEX_NAME).search(query=search.Query(
            query_string=query_string, options=query_options))

    for result in results:
        rcsid = result.doc_id
        r = Person.get_by_id(rcsid)
        if r:
            per = Person.buildMap(r)
            per['name'] = per['name'].title()
            data.append(per)
    d["data"] = data
    s = json.dumps(d)
    self.response.out.write(s)


app = webapp2.WSGIApplication([
    ("/api", Api)
  ])

