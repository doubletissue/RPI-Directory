from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import rdbms
from google.appengine.api import memcache
import os
from google.appengine.ext.webapp import template
import logging
import operator
import re
import cgi

_INSTANCE_NAME = 'christianjohnson.org:rpidirectory:christianjohnson'

reg_b = re.compile(r"android.+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-", re.I|re.M)

class MainPage(webapp.RequestHandler):
  def get(self):
    #Check for mobile browser, send them to the Play Store
    user_agent = self.request.headers['User-Agent']
    url_to_go = "market://details?id=org.rpi.rpinfo"
    b = reg_b.search(user_agent)
    v = reg_v.search(user_agent[0:4])
    if b or v:
      self.redirect(url_to_go)
    
    #Check MemCache for number of people in website
    memcache_key = "number_people"
    cached_mem = memcache.get(memcache_key)
    if cached_mem is not None:
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
    if cached_mem is not None:
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
    if cached_mem is not None:
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
    if cached_mem is not None:
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
    if cached_mem is not None:
      list_of_last_names = cached_mem
    else:
      cursor.execute("SELECT last_name, COUNT(last_name) as total from rpidirectory  WHERE last_name NOT LIKE '<th>%' GROUP BY last_name ORDER BY total DESC LIMIT 20")
      last_names = cursor.fetchall()
      list_of_last_names = []
      for row in last_names:
        list_of_last_names.append((str(row[0]).title(), row[1]))
      memcache.add(memcache_key, list_of_last_names, TIME_MEMCACHE)
    
    #Most common first names searched
    memcache_key = "stats_first_names"
    cached_mem = memcache.get(memcache_key)
    if cached_mem:
      sorted_x = sorted(cached_mem.iteritems(), key=operator.itemgetter(1), reverse=True)
      list_of_searched_first_names = sorted_x[:20]
    else:
      list_of_searched_first_names = None
      
    #Most common last names searched
    memcache_key = "stats_last_names"
    cached_mem = memcache.get(memcache_key)
    if cached_mem is not None:
      sorted_x = sorted(cached_mem.iteritems(), key=operator.itemgetter(1), reverse=True)
      list_of_searched_last_names = sorted_x[:20]
    else:
      list_of_searched_last_names = None
      
    #List of IPs
    memcache_key = "stats_ip"
    cached_mem = memcache.get(memcache_key)
    if cached_mem is not None:
      sorted_x = sorted(cached_mem.iteritems(), key=operator.itemgetter(1), reverse=True)
      list_of_ips = sorted_x[:20]
    else:
      list_of_ips = None
    
    
    #MemCache Stats
    memcache_stats = memcache.get_stats()
    memcache_stats['bytes'] /= 1000.0
    
    template_values = {'memcache': memcache_stats,
                       'list_of_majors' : list_of_majors,
                       'list_of_classes' : list_of_classes,
                       'list_of_faculty' : list_of_faculty,
                       'list_of_first_names' : list_of_first_names,
                       'list_of_last_names' : list_of_last_names,
                       'list_of_searched_first_names' : list_of_searched_first_names,
                       'list_of_searched_last_names' : list_of_searched_last_names,
                       'list_of_ips' : list_of_ips,
                       'number_people' : memcache.get("number_people")
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
