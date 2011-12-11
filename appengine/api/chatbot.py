from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
from google.appengine.api import urlfetch
import urllib

import logging
import cgi
import urllib


class ChatHandler(xmpp_handlers.CommandHandler):
  def post(self):
    message = xmpp.Message(self.request.POST)
    query = message.body.lower()
    search_string = urllib.quote(query)
    message.reply("Searching...try again in a few seconds if I don't get back to you :)")
    url = 'http://rpidirectory.appspot.com/api?name=' + search_string + '&page_size=3&page_num=1'
    result = urlfetch.fetch(url)
    if result.status_code != 200:
      message.reply("An internal error occured, please try again in a few minutes.")
      return
    
    s = ''
    d = eval(result.content)
    for person in d['data']:
      s += '*' + person['name'] + "*\n"
      #s += '('

      if 'email' in person:
        s += person['email'] + '\n'
        
      if 'major' in person:
        s += person['major'] + '\n'
      elif 'department' in person:
        s += person['department'] + '\n'
      
      if 'year' in person:
        s += person['year'] + '\n'
      elif 'title' in person:
        s += person['title'] + '\n'
      else:
        s += 'Faculty\n'
      #s += ')\n'
    message.reply(s)



application = webapp.WSGIApplication([
    ("/_ah/xmpp/message/chat/", ChatHandler)
  ])
   
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()