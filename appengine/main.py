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
    conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
    cursor = conn.cursor()
    
    #Majors
    cursor.execute("SELECT major, COUNT(major) as total FROM rpidirectory GROUP BY major ORDER BY total DESC LIMIT 20")
    majors = cursor.fetchall()
    list_of_majors = []
    for row in majors:
      list_of_majors.append((str(row[0]).title(), row[1]))
    
    #Classes - LIMIT 5 to eliminate NULL and NONE values
    cursor.execute("SELECT year, COUNT(year) as total FROM rpidirectory GROUP BY year ORDER BY total DESC LIMIT 5")
    classes = cursor.fetchall()
    list_of_classes = []
    for row in classes:
      list_of_classes.append((str(row[0]).title(), row[1]))
      
   #Faculty - LIMIT 20
    cursor.execute("SELECT department, COUNT(department) from rpidirectory GROUP BY department ORDER BY COUNT(department) DESC LIMIT 20")
    faculties = cursor.fetchall()
    list_of_faculty = []
    for row in faculties:
      list_of_faculty.append((str(row[0]).title(), row[1]))
    
    #MemCache Stats
    memcache_stats = memcache.get_stats()
    memcache_stats['bytes'] /= 1000.0
    
    template_values = {'memcache': memcache_stats,
                       'list_of_majors' : list_of_majors,
                       'list_of_classes' : list_of_classes,
                       'list_of_faculty' : list_of_faculty,
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
