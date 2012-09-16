import urllib2
import time

def get_page(key):
  url = "http://prod3.server.rpi.edu/peopledirectory/entry.do?datasetName=directory&key=" + str(key)

  sleep_time = 0.1
  while True:
    try:
      result = urllib2.urlopen(url)
      break;
    except urllib2.URLError:
      print "Sleeping for...",sleep_time
      time.sleep(sleep_time)
      sleep_time = sleep_time*2
      if sleep_time > 300:
        sleep_time = 300

  return result.read()

def is_valid_result(page):
  if "wrong state" in page:
    return False
  else:
    return True

prev_valid = False
results = open("results.txt", "w")
for i in range(20000):
  if i % 1 == 0:
    print i
  current_valid = is_valid_result(get_page(i))
  if prev_valid == True and current_valid == False:
    results.write("start missing: " + str(i) + "\n")
  elif prev_valid == False and current_valid == True:
    results.write("start present: " + str(i) + "\n")
  prev_valid = current_valid