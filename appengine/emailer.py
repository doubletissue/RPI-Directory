from google.appengine.api import mail
import logging

SENDER = "do-not-reply@rpidirectory.appspotmail.com"
ACTIVATION_SUBJECT = "Link your account on RPI directory." 
ACTIVATION_BODY = """
To activate your account, visit the following this link: http://rpidirectory.appspot.com/dashboard?activation={0}

This RCS account was claimed by: {1}.  If this is not you, please visit http://rpidirectory.appspot.com to claim your account.

Best,
The RPI Directory Team

Web: http://rpidirectory.appspot.com/
Chat Bot: Add rpidirectory@rpidirectory.appspotchat.com to your Gmail chat list
Android App: https://play.google.com/store/apps/details?id=org.rpi.rpinfo
iPhone/iPad App: http://itunes.apple.com/us/app/rpi-directory/id519895392
"""

def send_activation_email(person, user, activation_code):
  # Don't spam the president...
  if person.rcsid == "president":
    return False
  body = ACTIVATION_BODY.format(activation_code, user.email())
  logging.info('Email body: ' + body)
  mail.send_mail(SENDER, person.email, ACTIVATION_SUBJECT, body)
  return True
