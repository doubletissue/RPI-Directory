import datetime
import logging
import re
import urllib
import webapp2
import string
import simplejson as json

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
from models import SuggestObject
from models import StatsObject

suggest_attributes = [
  'major',
  'department',
  'first_name',
  'last_name',
  'year',
  'title',
  'prefered_name'
]

def makeSubstrings(s):
  if not s:
    return []
  s = str(s)
  r = []
  #for i in range(len(s)):
  #   for j in range(i + 1, len(s) + 1):
  #      r.append(str(s[i:j]))
  for i in range(len(s)):
          r.append(str(s[:i+1]))
  return r

def process_string(s):
  for c in string.punctuation:
    s = s.replace(c, ' ')
  while s.find('  ') >= 0:
    s = s.replace('  ',' ')
  l = s.replace('\n', ' ').split()
  l = list(set(l))
  return l

def suggest_map(data):

    logging.info(data.name)
    logging.info(str(data.json))
    d = eval(str(data.json))

    s = str(data.name)
    
    for i in suggest_attributes:
        if i in d:
            dic = d[i][i]
            num = 0
            for v in dic:
                num += int(dic[v])
            for j in makeSubstrings(s):
                logging.info("MAP: Yield %s -> {%s, %s}" % (j,s,str(num)))
                yield j,{s:num}
            
'''
    d = Person.buildMap(data)
    logging.info("MAP: Got %s", str(d))
    wordSet = set()
    for k,v in d.items():
        if k not in suggest_attributes:
            continue
        for i in process_string(v):
            wordSet.add(i)
    for i in wordSet:
        for j in makeSubstrings(i):
            logging.info("MAP: Yield %s -> %s" % (j,i))
            yield j,{i:1}
'''
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

def suggest_reduce(key, values):
  d = {}
  logging.info("REDUCE: Got " + str(key) + ' --> ' + str(values))
  for v in values:
    logging.info("REDUCE: Adding %s",str(v))
    v = eval(v)
    d = update_dict(d,v)
  logging.info('REDUCE FINAL: ' + str(key) + " --> " + str(d))
  #yield "%s: %s\n" % (str(key), str(d))
  entity = SuggestObject(id = key)
  entity.name = key
  entity.json = d
  yield op.db.Put(entity)

class SuggestPipeline(base_handler.PipelineBase):

  def run(self):
    output = yield mapreduce_pipeline.MapreducePipeline(
        "suggest",
        "cron.suggest.suggest_map",
        "cron.suggest.suggest_reduce",
        "mapreduce.input_readers.DatastoreInputReader",
        "mapreduce.output_writers.BlobstoreOutputWriter",
        mapper_params={
            "entity_kind": 'models.StatsObject',
            'namespace':''
        },
        reducer_params={
            "mime_type": "text/plain",
        },
        shards=8)

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
    pipeline = SuggestPipeline()

    pipeline.start()
    self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)

  def post(self):
    pipeline = StatsPipeline()

    pipeline.start()
    self.redirect(pipeline.base_path + "/status?root=" + pipeline.pipeline_id)
    

app = webapp2.WSGIApplication(
    [
        ('/sure', IndexHandler)
    ],
    debug=True)
