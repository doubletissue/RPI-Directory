import datetime
import logging
import re
import urllib
import webapp2
import string

from google.appengine.ext import blobstore
from google.appengine.ext import db

from google.appengine.ext.webapp import blobstore_handlers

from mapreduce.lib import files
from google.appengine.api import taskqueue
from google.appengine.api import users

from mapreduce import base_handler
from mapreduce import mapreduce_pipeline
from mapreduce import operation as op
from mapreduce import shuffler

from models import Person
from models import StatsObject


base_stats_attributes = [
  'major',
  'department',
  'first_name',
  'last_name',
  'year',
  'title',
]

info_stats_attributes = [
  'major',
  'department',
  'first_name',
  'last_name',
  'year',
  'title',
]

def process_string(s):
  for c in string.punctuation:
    s = s.replace(c, ' ')
  while s.find('  ') >= 0:
    s = s.replace('  ',' ')
  l = s.replace('\n', ' ').split()
  return l

def stats_map(data):

    d = Person.buildMap(data)
    logging.info("MAP: Got %s", str(d))
    for k,v in d.items():
      if not k or not v or k not in base_stats_attributes:
        continue
      logging.info("MAP GLOBAL: " + str(k) + ' --> ' + str(v))
      yield k, {v:1}
      r = {k:{}}
      for k2,v2 in d.items():
        if not k2 or not v2 or k == k2 or k2 not in info_stats_attributes:
          continue
        # Ex: First name = Dan, Major = CS
        # For the string 'Dan', when it is used as a first name,
        # Has _x_ CS Majors
        r[k][k2] = {v2:1}
      s = str(v)
      logging.info('MAP FINAL: ' + s + ' --> ' + str(r))
      yield s,r
      l = process_string(s)
      if len(l) > 1:
        for i in l:
          yield i,r

# We know all dicts will be mapping from a string to either a dict or an int
def update_dict(d,d2):
  if type(d2) == type(1):
    return d + d2
  for k in d2:
    if k in d:
      d[k] = update_dict(d[k],d2[k])
    else:
      d[k] = d2[k]
  return d

def stats_reduce(key, values):
  d = {}
  logging.info("REDUCE: Got " + str(key) + ' --> ' + str(values))
  for v in values:
    logging.info("REDUCE: Adding %s",str(v))
    v = eval(v)
    d = update_dict(d,v)
  logging.info('REDUCE FINAL: ' + str(key) + " --> " + str(d))
  #yield "%s: %s\n" % (str(key), str(d))
  entity = StatsObject(id = key)
  entity.name = key
  entity.json = d
  yield op.db.Put(entity)

class StatsPipeline(base_handler.PipelineBase):

  def run(self):
    output = yield mapreduce_pipeline.MapreducePipeline(
        "statistics",
        "mr.stats.stats_map",
        "mr.stats.stats_reduce",
        "mapreduce.input_readers.DatastoreInputReader",
        "mapreduce.output_writers.BlobstoreOutputWriter",
        mapper_params={
            "entity_kind": 'models.Person',
            'namespace':''
        },
        reducer_params={
            "mime_type": "text/plain",
        },
        shards=1)

    yield StoreOutput(output)


class StoreOutput(base_handler.PipelineBase):
  """A pipeline to store the result of the MapReduce job in the database.

  Args:
    mr_type: the type of mapreduce job run (e.g., WordCount, Index)
    encoded_key: the DB key corresponding to the metadata of this job
    output: the blobstore location where the output of the job is stored
  """

  def run(self,output):
    logging.info("output is %s" % str(output))
    
    
    
class IndexHandler(webapp2.RequestHandler):

  def get(self):
    pipeline = StatsPipeline()

    pipeline.start()
    #self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)

  def post(self):
    pipeline = StatsPipeline()

    pipeline.start()
    #self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)
    

app = webapp2.WSGIApplication(
    [
        ('/ahoy', IndexHandler)
    ],
    debug=True)
