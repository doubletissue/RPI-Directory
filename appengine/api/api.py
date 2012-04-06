from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import rdbms
from google.appengine.api import memcache
import logging
import cgi
import urllib
from models import Person
from django.utils import simplejson as json

_INSTANCE_NAME = 'christianjohnson.org:rpidirectory:christianjohnson'
QUERY_LIMIT = 20

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
  if row_attributes[0] != None and row_attributes[1] != None:
    output["name"] = cgi.escape(CamelCase(raw_row[0] + " " + raw_row[1]))

  #Parse the rest
  for attribute,raw_row_data in zip(row_attributes[2:], raw_row[2:]):
    if raw_row_data not in [None, "None"]:
      if attribute in ["department", "mailing_address", "office_location", "major", "title", "year"]:
        output[attribute] = cgi.escape(CamelCase(raw_row_data))
      else:
        output[attribute] = cgi.escape(raw_row_data)

  return output

class NewApi(webapp.RequestHandler):
  pass

def parse_int(i, default):
  if i == '':
    return default
  else:
    return int(i)

class Api(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    year      = urllib.unquote(cgi.escape(self.request.get('year')).lower()[:50])
    major     = urllib.unquote(cgi.escape(self.request.get('major')).lower()[:50])
    name      = urllib.unquote(cgi.escape(self.request.get('name')).lower()[:50])
    token     = urllib.unquote(cgi.escape(self.request.get('token')))
    page_num  = parse_int(urllib.unquote(cgi.escape(self.request.get('page_num'))), 1)
    page_size = parse_int(urllib.unquote(cgi.escape(self.request.get('page_size'))), 20)
    
    # Flood Prevention
    ip = str(self.request.remote_addr)
    ipCount = memcache.get(ip)
    if ipCount:
      if ipCount > 20:
        self.response.out.write("Error!")
        return
      memcache.replace(ip,ipCount+1,time=3600)
    else:
      memcache.add(ip,1,time=3600)
    
    #Check memcache for results
    memcache_key = name + ":" + major + ":" + year
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      d = {}
      d['data'] = cached_mem
      d['token'] = token
      d['name'] = name
      
      s = json.dumps(d)
      self.response.out.write(s)
      return
    
    # If not, we query Cloud SQL
    conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
    cursor = conn.cursor()
    
    names = map(str, name.split()[:3])

    #Get the first name and the last name. Ignore other things.
    if len(names) == 1:
      #Check for RCS ID
      #logging.debug("Checking RCS ID...")
      rcsid_candidate = names[0]
      cursor.execute("SELECT " + ",".join(row_attributes) + " FROM rpidirectory WHERE rcsid = %s LIMIT %s,%s", (rcsid_candidate, (page_num-1)*20, QUERY_LIMIT))

      if cursor.rowcount == 0:
        #Check for partial name match
        #logging.debug("No RCS ID, checking name...")
        name_part = names[0] + '%'
        cursor.execute("SELECT " + ",".join(row_attributes) + " FROM rpidirectory WHERE first_name LIKE %s OR last_name LIKE %s LIMIT %s,%s", (name_part, name_part, (page_num-1)*20, QUERY_LIMIT))
    elif len(names) > 1:
      #Check for exact name match
      #logging.debug("Checking exact name match...")
      first_name = names[0]
      last_name = names[-1]
      cursor.execute("SELECT " + ",".join(row_attributes) + " FROM rpidirectory WHERE first_name = %s AND last_name = %s LIMIT %s,%s", (first_name, last_name, (page_num-1)*20, QUERY_LIMIT))
      
      if cursor.rowcount == 0:
        #Check for partial name match
        #logging.debug("No exact name match, checking partial name match...")
        first_name = names[0] + '%'
        last_name = names[-1] + '%'
        cursor.execute("SELECT " + ",".join(row_attributes) + " FROM rpidirectory WHERE first_name LIKE %s AND last_name LIKE %s LIMIT %s,%s", (first_name, last_name, (page_num-1)*20, QUERY_LIMIT))
    
    d = {}
    l = []
    
    if len(names) != 0 and cursor.rowcount != 0:
      for row in cursor.fetchall():
        l.append(parse_person_from_sql(row))
        """
        l.append({"name": cgi.escape(row[0]) + " " + cgi.escape(row[1]), 
                  "major": cgi.escape(row[2]),
                  "email": cgi.escape(row[3]),
                  "year": cgi.escape(row[4])})
        """
    
    d = {}
    d['data'] = l
    d['token'] = token
    d['name'] = name
    
    #Add to memcache
    memcache.add(memcache_key, l, 518400)
    
    logging.debug("Cache miss, adding " + name + " to MemCache")
    
    s = json.dumps(d)
    self.response.out.write(s)

application = webapp.WSGIApplication([
    ("/api", Api)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()