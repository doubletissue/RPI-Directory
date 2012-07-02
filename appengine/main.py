
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import operator

_INSTANCE_NAME = 'christianjohnson.org:rpidirectory:christianjohnson'

class MainPage(webapp.RequestHandler):
  def get(self):
    #Check for mobile browser, send them to the Play Store
    #user_agent = self.request.headers['User-Agent']
    #url_to_go = "market://details?id=org.rpi.rpinfo"
    #b = reg_b.search(user_agent)
    #v = reg_v.search(user_agent[0:4])
    #if b or v:
    #  self.redirect(url_to_go)

    #Check MemCache for number of people in website
    memcache_key = "number_people"
    cached_mem = memcache.get(memcache_key)
    if cached_mem is not None:
      number_people = cached_mem
    else:
      #TODO (christian): Calculate total number of people
      number_people = 11712

    #Store it in MemCache
    memcache.add(memcache_key, number_people, 43200)

      #Commify number
      r = []
      for i, c in enumerate(str(number_people)[::-1]):
        if i and (not (i % 3)):
          r.insert(0, ',')
        r.insert(0, c)
      number_people = ''.join(r)

    template_values = {"number_people": number_people}
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class Stats(webapp.RequestHandler):
  def get(self):
    TIME_MEMCACHE = 172800
    cursor = None
    conn = None
    #Majors
    #Check MemCache
    memcache_keys = ["stats_major",
                     "stats_classes",
                     "stats_faculty",
                     "stats_first_name",
                     "stats_last_name",
                     "stats_ip",
                     "number_people"]

    cached_mem = memcache.get_multi(memcache_keys)
    memcache_key = "stats_major"
    if memcache_key in cached_mem:
      list_of_majors = cached_mem[memcache_key]
    else:
      conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
      cursor = conn.cursor()
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
    if memcache_key in cached_mem:
      list_of_classes = cached_mem[memcache_key]
    else:
      if not cursor:
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
        cursor = conn.cursor()
      cursor.execute("SELECT year, COUNT(year) as total FROM rpidirectory GROUP BY year ORDER BY total DESC LIMIT 5")
      classes = cursor.fetchall()
      list_of_classes = []
      for row in classes:
        list_of_classes.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_classes, TIME_MEMCACHE)

    #Faculty - LIMIT 20
    #Check MemCache
    memcache_key = "stats_faculty"
    if memcache_key in cached_mem:
      list_of_faculty = cached_mem[memcache_key]
    else:
      if not cursor:
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
        cursor = conn.cursor()
      cursor.execute("SELECT department, COUNT(department) from rpidirectory GROUP BY department ORDER BY COUNT(department) DESC LIMIT 20")
      faculties = cursor.fetchall()
      list_of_faculty = []
      for row in faculties:
        list_of_faculty.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_faculty, TIME_MEMCACHE)

    #First Name Stats
    #Check MemCache
    memcache_key = "stats_first_name"
    if memcache_key in cached_mem:
      list_of_first_names = cached_mem[memcache_key]
    else:
      if not cursor:
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
        cursor = conn.cursor()
      cursor.execute("SELECT first_name, COUNT(first_name) as total from rpidirectory WHERE first_name <> 'id=\"singledirectoryentry\">' GROUP BY first_name ORDER BY total DESC LIMIT 20")
      first_names = cursor.fetchall()
      list_of_first_names = []
      for row in first_names:
        list_of_first_names.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_first_names, TIME_MEMCACHE)


    #Last Name Stats
    #Check MemCache
    memcache_key = "stats_last_name"
    if memcache_key in cached_mem:
      list_of_last_names = cached_mem[memcache_key]
    else:
      if not cursor:
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='rpidirectory')
        cursor = conn.cursor()
      cursor.execute("SELECT last_name, COUNT(last_name) as total from rpidirectory  WHERE last_name NOT LIKE '<th>%' GROUP BY last_name ORDER BY total DESC LIMIT 20")
      last_names = cursor.fetchall()
      list_of_last_names = []
      for row in last_names:
        list_of_last_names.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_last_names, TIME_MEMCACHE)

    #List of IPs
    memcache_key = "stats_ip"
    if memcache_key in cached_mem:
      sorted_x = sorted(cached_mem[memcache_key].iteritems(), key=operator.itemgetter(1), reverse=True)
      list_of_ips = sorted_x[:20]
    else:
      list_of_ips = None

    #MemCache Stats
    memcache_stats = memcache.get_stats()
    memcache_stats['bytes'] /= 1000.0

    #Num people check
    if "number_people" not in cached_mem:
      cached_mem["number_people"] = 11519


    template_values = {'memcache': memcache_stats,
                       'list_of_majors' : list_of_majors,
                       'list_of_classes' : list_of_classes,
                       'list_of_faculty' : list_of_faculty,
                       'list_of_first_names' : list_of_first_names,
                       'list_of_last_names' : list_of_last_names,
                       #'list_of_searched_first_names' : list_of_searched_first_names,
                       #'list_of_searched_last_names' : list_of_searched_last_names,
                       'list_of_ips' : list_of_ips,
                       'number_people' : cached_mem["number_people"]
                       }

    path = os.path.join(os.path.dirname(__file__), 'stats.html')
    self.response.out.write(template.render(path, template_values))

    if conn:
      conn.close()

application = webapp.WSGIApplication(
  [('/', MainPage),
   ('/stats', Stats), ])

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
