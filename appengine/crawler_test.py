from urllib import urlopen

def getPage( key ):
  url = "http://prod3.server.rpi.edu/peopledirectory/entry.do?datasetName=directory&key=" + str(key)
  return urlopen(url).read()
  
def findAttribute(string, attribute):
  
  startIndex = string.find(attribute)
  endIndex   = string.find('</td>',startIndex) + len('</td>')
  
  if startIndex < 0:
    return ""
  if string[startIndex:endIndex].find("<td />") > 0:
    return ""
  else:
    startIndex = string.find('<td>',startIndex)
    startIndex = string.find('>',startIndex) + 1
    endIndex   = string.find('</td>',startIndex)
    r = string[startIndex:endIndex].strip()
    r = r.replace("<br />","\n")
    return r
    
def findName(string):
  startIndex = string.find('<th class="name">')
  startIndex = string.find('>',startIndex) + 1
  endIndex   = string.find('</th>',startIndex)
  return string[startIndex:endIndex].strip()

def findHomepage(string):
  homepage = findAttribute(string,"Homepage:")
  if homepage is "":
    return ""
  startIndex = homepage.find('"') + 1
  endIndex   = homepage.find('"',startIndex)
  return homepage[startIndex:endIndex].strip()
  
  
def findEmail(string):
  email = ""
  startIndex = 0
  imagePath = "http://www.rpi.edu/dept/cct/apps/csvdata/directory/resources/glyphs/"
  while True:
    if string.find(imagePath,startIndex) < 0:
      break
    startIndex = string.find(imagePath, startIndex) + len(imagePath)
    endIndex   = string.find(".gif", startIndex)
    
    letterID = int(string[startIndex:endIndex].strip())
    if letterID == 99:
      email += '@rpi.edu'
    elif letterID < 28:
      email += chr(letterID+96)
    else:
      email += str(letterID-28)
  return email
  
def findStuff( string ):
  
  d = {}
  
  attributes = {
                  'Class:'           : 'class',
                  'Curriculum:'      : 'major',
                  'Title:'           : 'title',
                  'Telephone:'       : 'phone',
                  'Fax:'             : 'fax',
                  'Office Location:' : 'office location',
                  'Campus Mailstop:' : 'campus mailstop',
                  'Mailing Address:' : 'mailing address'
                }
  
  string = string[string.find('id="singleDirectoryEntry"'):]
  string = string[:string.find('</table')]
  
  d['name'] = findName(string)
  
  homepage = findHomepage(string)
  if homepage is not "":
    d['homepage'] = findHomepage(string)
  
  email = findEmail(string)
  if email is not "":
    d['email'] = email
  
  for k in attributes.keys():
    v = findAttribute(string,k)
    if v is not "":
      d[attributes[k]] = v
  
  for k in d.keys():
    print k,"-->",d[k]
  print "-------------------------"
  
  

def parseData( key ):
  s = getPage(key)
  findStuff(s)

#parseData(4991)
for key in range(4000,5000):
  print key
  parseData(key)