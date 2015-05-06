__author__ = 'CassyLee'

from datetime import datetime
from elasticsearch import Elasticsearch
import json
import time
# by default we connect to localhost:9200

class ES_query(object):

    def __init__(self):
        self.es = Elasticsearch()

#load schema and create an index
    def create_index(self,index_name):
        with open('sportsman_schema.txt','r') as schema:
            sports_schema = json.load(schema)
        #if self.es.indices.exists:
        self.es.indices.delete(index=index_name)
        novel_index = self.es.indices.create(index = index_name, body = sports_schema)


    #bulk load the data
    def bulk_loading(self):
        with open('onthesnowplace.json','r') as j:
            json_text = json.load(j)
        bulk_file = []
        action = { "index": { "_index": "i_sportsman", "_type": "stadium" }}

        for i in range(len(json_text)):
            bulk_file.append(action)
            bulk_file.append(json_text[i])
                #return bulk_file

        #call create_index function to create i_novel index
        self.create_index("i_sportsman")
        bulk_load = self.es.bulk(body = bulk_file)
        self.es.indices.refresh(index = "i_sportsman")
        return bulk_load

    def q_mwf(self,string2,num1,num2):
        query_body = {"query" : {
            "filtered" : {
                "query": {
                        "bool" : {
                            "must": [{"match": {"activity_types": string2}}],
                            #"should": {"match": {"text" : string2} },
                            "boost" : 1.0}},
                "filter" : {
                    "geo_distance" : {
                        "distance" : "500km",
                        "geo_location" : {
                            "lat" : num1,
                            "lon" : num2
                        }
                    }}
            }
        }}

        res = self.es.search(index = "i_sportsman", doc_type = "stadium", body = query_body,size = 10000)
        return res
        # self.prints(res)

    #print the required results by order
    def prints(self,res):
        hits = res["hits"]["hits"]
        print 'totle number of hits: ' + str(len(hits))
        for i in range(min(10,len(hits))):
            print '\n'
            print 'rank: ' + str(i+1)
            stadium = hits[i]["_source"]



if __name__ == "__main__":
    x =  ES_query()
    x.bulk_loading()
    print x.q_mwf('ski',42.3744753,-71.2492378)
