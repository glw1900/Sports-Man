from django.http import *
from django.http import HttpResponse
from django.template import RequestContext
from ElasticSearch.Esearch import ES_query
from django.shortcuts import render
from .models import SportType
from django.shortcuts import render_to_response
import socket
import json
from search.toGolocation import to_golocation

def index(request):
    sportType = SportType.objects.all()
    if 'Court_Name' in request.POST and 'selectedType' in request.POST:
        to_search = request.POST['Court_Name']
        selectedType = request.POST['selectedType']
        location = to_golocation(to_search)
        lat = location['lat']
        lng = location['lng']
        q = ES_query()
        hits = q.q_mwf(selectedType.lower(),lat,lng)
        output = []
        for i in range(min(10,len(hits['hits']['hits']))):
            res = hits['hits']['hits']
            temp = 'rank: ' + str(i+1)
            stadium = res[i]["_source"]
            temp = temp + '     name: ' + stadium['name']
            output.append(temp)
        print len(output)
        return render(request,'search/index.html',{'sportType':sportType, 'searchText':to_search,'output':output})
    else:
        return render(request,'search/index.html',{'sportType':sportType})



