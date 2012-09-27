import logging
import random
import time

from google.appengine.api.memcache import Client as mcClient

mc = mcClient()
NS = "mtx"

class Mutex:
  """Simple mutex mechanism.
  
  A fork of:
  http://appengine-cookbook.appspot.com/recipe/mutex-using-memcache-api/
  
  Example use:
    m = Mutex("Some Key", 2)
    try:
      m.lock()
      # Do stuff here....
    except:
      # Handle errors here....
      pass
    finally:
      m.unlock()
  """
  def __init__(self, key, mem_timeout=30):
    self.key = key
    self.mem_timeout = mem_timeout
    self.locked = False
    random.seed()
  
  def __del__(self):
    if self.locked == True:
      self.unlock()
  
  def lock(self):
    if self.locked == True:
      return
    did_add = mc.add(self.key, True, time=self.mem_timeout, namespace=NS)
    while did_add is False:
      logging.info("MUTEX: waiting (key==%s)" % (self.key))
      time.sleep(random.random() * 1) # average .5 second wait
      did_add = mc.add(self.key, True, time=self.mem_timeout, namespace=NS)
    logging.info("MUTEX: acquired lock (key==%s)" % (self.key))
    self.locked = True
  
  def unlock(self):
    if self.locked == True:
      mc.delete(self.key, namespace=NS)
      logging.info("MUTEX: released lock (key==%s)" % (self.key))
      self.locked = False
