from google.appengine.api import mail
from datetime import datetime, timedelta

SENDER = "do-not-reply@rpidirectory.appspotmail.com"
ACTIVATION_SUBJECT = "Link to your account on RPI directory."
ACTIVATION_BODY = """
To activate your account, visit the following this link: http://test-mail.rpidirectory.appspot.com/dashboard?activate={}
"""
ONE_DAY = timedelta(days=1)

def parse_email_from_rcs(person):
  if person.email:
    return person.email
  else:
    return person.rcs + "@rpi.edu"

def send_activation_email(account, person, activation_code):
  # If the user is doing too much updating
  if (account.date_emailed > datetime.now()-ONE_DAY or
      account.date_emailed > datetime.now()-ONE_DAY):
      return False
  # Don't spam the president...
  if person.title == "President":
    return False
  mail.send_mail(SENDER, 
                 parse_email_from_rcs(person),
                 ACTIVATION_SUBJECT, 
                 ACTIVATION_BODY.format(activation_code))
  account.date_emailed = datetime.now()
  person.date_emailed = datetime.now()
  account.put()
  person.put()
  return True