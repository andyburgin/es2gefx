# Tool to extract logstash data from elasticsearch and convert to a gexf file
#
# es2gexf queries elasticsearch and retrieves entries matching specified criteria (as nodes),
# it then identifies edges between the event nodes using defined parameters and finally uses 
# the pygexf library to generate a gexf file for importing into gephi.
#
# Please see http://data.andyburgin.co.uk/post/65706647269/visualising-logstash-apache-data-in-gephi for more details for how this tool has been used.
#

import elasticsearch
import sys
import os
import time
import datetime
from xml.sax.saxutils import escape
sys.path.append('gexf')
from _gexf import Gexf, GexfImport

# define Event class to hold evnet data from elastic search 
class Event(object):
    id = ""
    eventtype = ""
    source_host = ""
    source_path = ""
    message = ""
    timestamp = ""
    clientip = ""
    verb = ""
    response = ""
    request = ""
    bytes = "0"
    referrer = ""
    datetime = datetime.datetime.now()
    start = ""
    end = ""

    # constructor
    def __init__(self,hit):
      self.id = str(hit["_id"])
      self.eventtype = str(hit["_type"])
      self.source_host = str(hit["_source"]["@source_host"])
      self.source_path = str(hit["_source"]["@source_path"])
      self.message = str(hit["_source"]["@message"])
      self.timestamp = str(hit["_source"]["@timestamp"])
      fields = hit["_source"]["@fields"]
      self.clientip = fields["clientip"][0]
      self.response = fields["response"][0]
      if fields.get("request","") != "":
       self.request = fields["request"][0]
      else:
        self.request = ""
      if fields.get("verb","") != "":
        self.verb = fields["verb"][0]
      else:
        self.verb = ""   
      if fields.get("bytes","") != "":
        self.bytes = fields["bytes"][0]
      else:
        self.bytes = 0       
      if fields.get("agent","") != "":
        self.agent = fields["agent"][0]
      else:
        self.agent = ""  
      self.referrer = fields["referrer"][0]
      self.datetime = time.strptime(self.timestamp[:19],"%Y-%m-%dT%H:%M:%S")
      self.start = time.strftime("%Y-%m-%dT%H:%M:%S.000",self.datetime)
      t = time.mktime(self.datetime)
      t = t + relatetimeout 
      self.end = time.strftime("%Y-%m-%dT%H:%M:%S.000",time.localtime(t))
	  
    def toString(self):
      return str("id="+self.id+" timestamp="+str(self.datetime)+" eventtype="+self.eventtype+" response="+self.response+" source_host="+self.source_host+" source_path="+self.source_path+" message="+self.message)


# used to strip non alpha numberic utf chars from utf 16 strings
def stripped(x):
	return "".join([i for i in x if ord(i) in range(32, 127)])

# logging function
def log(msg):
  if verbose == True:
	print(msg)


### TODO: convert parameters to command line args
### parameters

# elasticsearch
host="192.168.2.220"
port="9200"

#date range
starttime = time.strptime("20131014000000","%Y%m%d%H%M%S")
endtime  = time.strptime("20131014080000","%Y%m%d%H%M%S")

# event type matching the @type to be returned from elasticsearch
evttype = "apache-access"


# field and time period to be used for edge detection
relatedfield = "clientip"
relatetimeout = 5

# debug messages ?
verbose = True


# create the graph
gexf = Gexf("es2gexf","logstash graph")
graph=gexf.addGraph("directed","dynamic","logstash graph","dateTime")

# define the node attributes in the graph
attrType = graph.addNodeAttribute("type", "null", "String","static","type")
attrMessage = graph.addNodeAttribute("message", "null", "String","static","message")
attrSource_host = graph.addNodeAttribute("source_host", "null", "String","static","source_host")
attrSource_path = graph.addNodeAttribute("source_path", "null", "String","static","source_path")	  
attrClientip = graph.addNodeAttribute("clientip", "null", "String","static","clientip")
attrVerb = graph.addNodeAttribute("verb", "null", "String","static","verb")
attrResponse = graph.addNodeAttribute("response", "null", "integer","static","response")
attrRequest = graph.addNodeAttribute("request", "null", "String","static","request")
attrBytes = graph.addNodeAttribute("bytes", "null", "integer","static","bytes")
attrAgent = graph.addNodeAttribute("agent", "null", "String","static","agent")
attrReferrer = graph.addNodeAttribute("referrer", "null", "String","static","referrer")

# query elasticsearch for all entries matching evttype, then add each entry as an Event to eventlist
eventlist = []
es = elasticsearch.Elasticsearch([host+":"+port])
resp=es.search(index="", body={"query": {"term": {"_type": {"value": evttype}}}}, search_type='scan', scroll='5m')
scroll_id = resp['_scroll_id']
ct = 0
while True:
  resp = es.scroll(scroll_id, scroll='5m')
  if not resp['hits']['hits']:
    break
  for hit in resp['hits']['hits']:
    evt = Event(hit)
    # check event is within time frame - add it if it is
    if evt.datetime > starttime and evt.datetime < endtime:
      eventlist.append(evt)
      ct = ct + 1
      log("adding event "+str(ct))
  scroll_id = resp['_scroll_id']


# sort the eventlist by start field
log("sorting list")
eventlist = sorted(eventlist, key=lambda event: event.start)
log("list sorted")

#itterate through events and add them as nodes to the graph
ct = 0
for evt in eventlist:
    ct = ct + 1
    n=graph.addNode(evt.id,str(evt.start)+" "+evt.clientip+" "+ evt.response+" "+evt.request+" "+evt.agent, evt.start, evt.end)
    n.addAttribute(attrType,evt.eventtype)
    n.addAttribute(attrMessage,stripped(evt.message))
    n.addAttribute(attrSource_host,evt.source_host)
    n.addAttribute(attrSource_path,evt.source_path)
    n.addAttribute(attrClientip,evt.clientip)
    n.addAttribute(attrVerb,evt.verb)
    n.addAttribute(attrResponse,evt.response)
    n.addAttribute(attrRequest,evt.request)
    n.addAttribute(attrBytes,evt.bytes)
    n.addAttribute(attrAgent,evt.agent)
    n.addAttribute(attrReferrer,evt.referrer)
    log("adding node "+str(ct)+" start="+str(evt.start)+" end="+str(evt.end))
    
#itterate and find events that match relatedfield within relatetimeout, generate corresponding edge
ct=0
edgecount = 0
for idx, event in enumerate(eventlist):
  ct = ct + 1
  log("checking event "+str(ct))
  for checkidx in range(idx+1, len(eventlist)-1):
    if getattr(event,relatedfield) == getattr(eventlist[checkidx],relatedfield):
      eventtime = time.mktime(event.datetime)
      chkeventtime = time.mktime(eventlist[checkidx].datetime)
      if chkeventtime < (eventtime + relatetimeout):
        edgecount = edgecount + 1
        log("edge found between "+str(idx)+" and "+str(checkidx))
        graph.addEdge(eventlist[idx].id+eventlist[checkidx].id,eventlist[idx].id,eventlist[checkidx].id)
        break

#futile attempt to clear some memory before writing file
del eventlist[:]

#output gexf file
log("writing gexf")
output_file=open("logstash.gexf","w")
gexf.write(output_file)

