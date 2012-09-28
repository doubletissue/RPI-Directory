from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
import cgi
import re
import webapp2
import string

class Crawler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    d = self.parseData(cgi.escape(self.request.get('key')))
    for k in d.keys():
      self.response.out.write(k + " --> " + str(d[k]) + '\n')
    self.response.out.write("-------------------------")

  def getMap(self, key):
    return self.parseData(key)

  def getPage(self, key):
    url = "http://prod3.server.rpi.edu/peopledirectory/entry.do?datasetName=directory&key=" + str(key)
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      logging.error("Failed to fetch URL: " + url + "; Error code: " + str(result.status_code))
      return ""

    return result.content

  def findAttribute(self, string, attribute):

    startIndex = string.find(attribute)
    endIndex = string.find('</td>', startIndex) + len('</td>')

    if startIndex < 0:
      return ""
    if string[startIndex:endIndex].find("<td />") > 0:
      return ""
    else:
      startIndex = string.find('<td>', startIndex)
      startIndex = string.find('>', startIndex) + 1
      endIndex = string.find('</td>', startIndex)
      r = string[startIndex:endIndex].strip()
      r = r.replace("&Amp;", "and")
      r = r.replace("&amp;", "and")
      r = r.replace("<br />", "\n")
      p = re.compile(' *\n *')
      r = p.sub('\n', r)
      p = re.compile('<.*?>')
      r = p.sub('', r)
      return r.lower()

  def findName(self, string):
    startIndex = string.find('<th class="name">')
    startIndex = string.find('>', startIndex) + 1
    endIndex = string.find('</th>', startIndex)
    return string[startIndex:endIndex].strip().lower()

  def findHomepage(self, string):
    homepage = self.findAttribute(string, "Homepage:")
    if homepage is "":
      return ""
    startIndex = homepage.find('"') + 1
    endIndex = homepage.find('"', startIndex)
    return homepage[startIndex:endIndex].strip().lower()


  def findEmail(self, string):
    email = ""
    startIndex = 0
    imagePath = "http://www.rpi.edu/dept/cct/apps/csvdata/directory/resources/glyphs/"
    while True:
      if string.find(imagePath, startIndex) < 0:
        break
      startIndex = string.find(imagePath, startIndex) + len(imagePath)
      endIndex = string.find(".gif", startIndex)

      letterID = int(string[startIndex:endIndex].strip())
      # Stop at @rpi.edu
      if letterID == 99:
        email += "@rpi.edu"
        break
      elif letterID == 39:
        email += '@'
      elif letterID == 38:
        email += '.'
      elif letterID < 28:
        # WTF RPI?
        if letterID == 22:
          letterID = 2
        if letterID > 22:
          letterID -= 1
        email += chr(letterID + 96)
      else:
        num = letterID - 27
        if num == 10:
          num = 0
        email += str(num)
    return email

  def findStuff(self, string):
    d = {}
    full_string = string
    attributes = {  'Class:'           : 'year',
                    'Curriculum:'      : 'major',
                    'Title:'           : 'title',
                    "Department"       : 'department',
                    'Telephone:'       : 'phone',
                    'Fax:'             : 'fax',
                    'Office Location:' : 'office_location',
                    'Campus Mailstop:' : 'campus_mailstop',
                    'Mailing Address:' : 'mailing_address'}

    if full_string.find('wrong state') >= 0:
      logging.warn("end of database!")
      return {'error':'end of database'}

    string = string[string.find('id="singleDirectoryEntry"'):]
    string = string[:string.find('</table')]

    if string is "":
      logging.warn("error reading data")
      return {'error':'page_not_found'}

    name = self.findName(string)
    if name is not "":
      names = name.split()[:3]
      if len(names) > 0:
        d['first_name'] = names[0]
      if len(names) > 1:
        d['last_name'] = names[-1]

    homepage = self.findHomepage(string)
    if homepage is not "":
      d['homepage'] = self.findHomepage(string)

    email = self.findEmail(string)
    if email is not "":
      d['email'] = email
      d['rcsid'] = d['email'].rsplit('@', 1)[0]

    for k in attributes.keys():
      v = self.findAttribute(string, k)
      if v is not "":
        d[attributes[k]] = v
    return d


  def parseData(self, key):
    s = self.getPage(key)
    d = self.findStuff(s)
    d['directory_id'] = str(key)
    return d

app = webapp2.WSGIApplication(
  [("/debugcrawl.*", Crawler)])
