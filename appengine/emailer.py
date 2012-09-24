from google.appengine.api import mail

SENDER = "RPI Directory"
ACTIVATION_SUBJECT = "Link to your account on RPI directory."
ACTIVATION_BODY = """
To activate your account, visit the following this link: {}
"""

def parse_email_from_rcs(rcs):
  return rcs + "@rpi.edu"

def send_activation_email(person, activation_code):
  mail.send_mail(SENDER, 
                 parse_email_from_rcs(person.rcs),
                 ACTIVATION_SUBECT, 
                 ACTIVATION_BODY.format(activation_code))