from google.appengine.api import mail

SENDER = "do-not-reply@rpidirectory.appspotmail.com"
ACTIVATION_SUBJECT = "Link to your account on RPI directory." 
ACTIVATION_BODY = """
To activate your account, visit the following this link: http://rpidirectory.appspot.com/dashboard?activation={}
"""


def send_activation_email(person, activation_code):
  # Don't spam the president...
  if person.title == "President":
    return False
  mail.send_mail(SENDER, person.email, ACTIVATION_SUBJECT + str(activation_code), 
                 ACTIVATION_BODY.format(activation_code))
  return True