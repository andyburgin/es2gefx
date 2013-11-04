es2gexf
=======

Overview
--------

es2gexf is a tool to extract logstash data from elasticsearch and convert to a gexf file

es2gexf queries elasticsearch and retrieves entries matching specified criteria (as nodes), it then identifies edges between the event nodes using defined parameters and finally uses the pygexf library to generate a gexf file for importing into gephi.

Please see http://data.andyburgin.co.uk/post/65706647269/visualising-logstash-apache-data-in-gephi for more details for how this tool has been used.


Fork it Fix it
--------------

This script has been written and tested against a single small logstash/elastic search server and is it's first release. At present I've used it to generate 25000 nodes with 18000 edges, there is a limit to what the xml libraries underlying pygexf can do (especially if you hit a "Killed" message when trying to write out the gexf file). 

Please feel free to fork, fix and push if you find errors.

BTW this is also the first peice of "real" Python development I've done so please excuse if I'm comitting any horendous Python faux-pas.

Comments and feed back welcome, just be nice :-)

Parameters
----------
I've marked this as a TODO, but the folowing parameters need to be changes to command line arguments. However for now you can edit them in the code.

* host & port - the ip and port number of elasticsearch url
* starttime & endtime - in format %Y%m%d%H%M%S includes all entries in elasticsearch within these timestamps
* evttype - the value of the @type field that indicates an elasticsearch entry generated logstash that match the %{COMBINEDAPACHELOG} grok pattern
* relatedfield & relatetimeout - field and time period to be used for edge detection
* verbose - debug messages

Requirements
------------

Built and tested with Python 2.7.3 on Debian Wheezy

Download the latest https://github.com/paulgirard/pygexf don't use the easy_install method as this will install 0.2.2 which is missing some of the newer features needed.


Credits
-------

Just a big shout out and thanks to the wonderful developers of:

* Logstash - http://logstash.net/
* Kibana - http://kibana.org/
* The Logstash cookbook - https://github.com/lusis/chef-logstash
* ElasticSearch - http://www.elasticsearch.org/
* Gephi - http://www.gephi.org/

