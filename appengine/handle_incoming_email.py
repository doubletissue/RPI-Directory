import logging
import webapp2
from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

SENDER = "feedback-bot@rpidirectory.appspotmail.com"

admins = ['christian@christianjohnson.org', 'jewishdan18@gmail.com', 'michorowitz@gmail.com']

class EmailHandler(InboundMailHandler):
  def receive(self, mail_message):
    for content_type, body in mail_message.bodies('text/html'):
      for m in admins:
        mail.send_mail(SENDER, m, "Feedback from %s: %s" % (mail_message.sender, mail_message.subject), body.decode())

app = webapp2.WSGIApplication([EmailHandler.mapping()])