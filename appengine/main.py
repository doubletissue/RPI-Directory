from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import rdbms
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import cgi

_INSTANCE_NAME = 'christianjohnson.org:rpidirectory:christianjohnson'

class MainPage(webapp.RequestHandler):
  def get(self):
    #Check MemCache for number of people in website
    memcache_key = "number_people"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      number_people = cached_mem
    else:
      #If not, we query Cloud SQL
      conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
      cursor = conn.cursor()
      cursor.execute("SELECT COUNT(*) FROM rpidirectory")
      number_people = cursor.fetchall()[0][0]

      #Commify number
      r = []
      for i, c in enumerate(str(number_people)[::-1]):
        if i and (not (i % 3)):
          r.insert(0, ',')
        r.insert(0, c)
      number_people = ''.join(r)
      
      #Store it in MemCache
      memcache.add(memcache_key, number_people, 43200)
    
    template_values = {"number_people": number_people}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class Stats(webapp.RequestHandler):
  def get(self):
    
    TIME_MEMCACHE = 86400
    
    conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
    cursor = conn.cursor()
    
    #Majors
    #Check MemCache
    memcache_key = "stats_major"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      list_of_majors = cached_mem
    else:
      cursor.execute("SELECT major, COUNT(major) as total FROM rpidirectory GROUP BY major ORDER BY total DESC LIMIT 20")
      majors = cursor.fetchall()
      list_of_majors = []
      for row in majors:
        list_of_majors.append((str(row[0]).title(), row[1]))
      
      #Store it in MemCache
      memcache.add(memcache_key, list_of_majors, TIME_MEMCACHE)
    
    
    #Classes - LIMIT 5 to eliminate NULL and NONE values
    #Check MemCache
    memcache_key = "stats_classes"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      list_of_classes = cached_mem
    else:
      cursor.execute("SELECT year, COUNT(year) as total FROM rpidirectory GROUP BY year ORDER BY total DESC LIMIT 5")
      classes = cursor.fetchall()
      list_of_classes = []
      for row in classes:
        list_of_classes.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_classes, TIME_MEMCACHE)
      
    #Faculty - LIMIT 20
    #Check MemCache
    memcache_key = "stats_faculty"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      list_of_faculty = cached_mem
    else:
      cursor.execute("SELECT department, COUNT(department) from rpidirectory GROUP BY department ORDER BY COUNT(department) DESC LIMIT 20")
      faculties = cursor.fetchall()
      list_of_faculty = []
      for row in faculties:
        list_of_faculty.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_faculty, TIME_MEMCACHE)
    
    #First Name Stats
    #Check MemCache
    memcache_key = "stats_first_name"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      list_of_first_names = cached_mem
    else:
      cursor.execute("SELECT first_name, COUNT(first_name) as total from rpidirectory WHERE first_name <> 'id=\"singledirectoryentry\">' GROUP BY first_name ORDER BY total DESC LIMIT 20")
      first_names = cursor.fetchall()
      list_of_first_names = []
      for row in first_names:
        list_of_first_names.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_first_names, TIME_MEMCACHE)
    
    
    #Last Name Stats
    #Check MemCache
    memcache_key = "stats_last_name"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      list_of_last_names = cached_mem
    else:
      cursor.execute("SELECT last_name, COUNT(last_name) as total from rpidirectory  WHERE last_name NOT LIKE '<th>%' GROUP BY last_name ORDER BY total DESC LIMIT 20")
      last_names = cursor.fetchall()
      list_of_last_names = []
      for row in last_names:
        list_of_last_names.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_last_names, TIME_MEMCACHE)
    
    
    #MemCache Stats
    memcache_stats = memcache.get_stats()
    memcache_stats['bytes'] /= 1000.0
    
    template_values = {'memcache': memcache_stats,
                       'list_of_majors' : list_of_majors,
                       'list_of_classes' : list_of_classes,
                       'list_of_faculty' : list_of_faculty,
                       'list_of_first_names' : list_of_first_names,
                       'list_of_last_names' : list_of_last_names,
                       }
                       
    path = os.path.join(os.path.dirname(__file__), 'stats.html')
    self.response.out.write(template.render(path, template_values))
    
    conn.close()

application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/stats', Stats),])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
