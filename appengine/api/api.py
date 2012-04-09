from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import rdbms
from google.appengine.api import memcache
from google.appengine.api import mail
import logging
import cgi
import urllib
from models import Person
from collections import defaultdict
from django.utils import simplejson as json

_INSTANCE_NAME = 'christianjohnson.org:rpidirectory:christianjohnson'

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
    search    = urllib.unquote(cgi.escape(self.request.get('q')).lower()[:100])
    token     = urllib.unquote(cgi.escape(self.request.get('token')))
    page_num  = parse_int(urllib.unquote(cgi.escape(self.request.get('page_num'))), 1)
    page_size = parse_int(urllib.unquote(cgi.escape(self.request.get('page_size'))), 20)
    
    if page_size > 20:
      page_size = 20
    
    # Flood Prevention
    ip = str(self.request.remote_addr)
    ipCount = memcache.get(ip)
    if ipCount is not None:
      if ipCount > 1000:
        d = {}
        d['data'] = 'Quota Exceeded'
        d['token'] = token
        d['q'] = search
        s = json.dumps(d)
        self.response.out.write(s)
        
        ban_time = 600 + 60 * 2 ** ( (ipCount-1000) )
        if ban_time > 7*24*60*60:
          ban_time = 7*24*60*60
        logging.info('Quota exceeded for ' + ip + ', count at ' + str(ipCount) + ', banned for ' + str(ban_time))
        memcache.replace(ip,ipCount+1,time=ban_time)
        
        if (ipCount - 1001) % 100 == 0:
          message = mail.EmailMessage(sender="IP Banning <ip-logger@rpidirectory.appspotmail.com>",
                                      subject="RPIDirectory IP " + ip + " Banned")
          message.to = "rpi-directory-ip@googlegroups.com"
          message.body = "IP: " + ip + "\nban time: " + str(ban_time) + "\nQuery: " + search + "\nHit Count: " + str(ipCount)
          message.send()
          logging.info("EMail sent about ip: " + ip) 
        return
      memcache.replace(ip,ipCount+1,time=600)
    else:
      memcache.add(ip,1,time=600)
      
    
    queries = map(str, search.split())
    #Check memcache for results
    memcache_key = ":".join(sorted(search.split()))
    cached_mem = memcache.get(memcache_key)
    if cached_mem is not None:
      d = {}
      d['data'] = cached_mem
      d['token'] = token
      d['q'] = search
      
      s = json.dumps(d)
      self.response.out.write(s)
      return
    
    # If not, we query Cloud SQL
    conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
    cursor = conn.cursor()
    

    query = 'SELECT ' + ",".join(row_attributes) + ' from rpidirectory WHERE ' 

    for word in queries:
      query += '('
      for field in query_attributes:
        query += field + ' LIKE ' + "'%" + word + "%'"
        if field is not query_attributes[-1]:
          query += ' OR '
      query += ')'
      if word is not queries[-1]:
        query += ' AND '
        
    query += ' ORDER BY first_name'
    query += ' LIMIT ' + str((page_num-1)*page_size) + ',' + str(page_size)
    
    logging.debug(query)
    
    cursor.execute(query)
    
    d = {}
    l = []
    
    if len(queries) != 0 and cursor.rowcount != 0:
      for row in cursor.fetchall():
        l.append(parse_person_from_sql(row))
    
    
    if len(l) > 0:
      #Log results in MemCache for Stats page
      #IP address
      ip = str(self.request.remote_addr)
      memcache_key = "stats_ip"
      cached_mem = memcache.get(memcache_key)
      if cached_mem is not None:
        cached_mem[ip] += 1
        memcache.set(memcache_key, cached_mem)
      else:
        d = defaultdict(int)
        d[ip] += 1
        memcache.set(memcache_key, d)
      
      ##Log names searched
      #if len(names) > 1 and len(names[0]) > 1 and len(names[-1]) > 1:
        ##First name
        #memcache_key = "stats_first_names"
        #cached_mem = memcache.get(memcache_key)
        #if cached_mem is not None:
          #cached_mem[names[0].title()] += 1
          #memcache.set(memcache_key, cached_mem)
        #else:
          #d = defaultdict(int)
          #d[names[0].title()] += 1
          #memcache.set(memcache_key, d)
      
        ##Last name
        #memcache_key = "stats_last_names"
        #cached_mem = memcache.get(memcache_key)
        #if cached_mem is not None:
          #cached_mem[names[-1].title()] += 1
          #memcache.set(memcache_key, cached_mem)
        #else:
          #d = defaultdict(int)
          #d[names[-1].title()] += 1
          #memcache.set(memcache_key, d)
    
    
    d = {}
    d['data'] = l
    d['token'] = token
    d['q'] = search
    
    #Add to memcache
    memcache_key = ":".join(sorted(search.split()))
    memcache.add(memcache_key, l, 518400)
    
    logging.debug("Cache miss, adding " + search + " to MemCache")
    
    s = json.dumps(d)
    self.response.out.write(s)

application = webapp.WSGIApplication([
    ("/api", Api)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()