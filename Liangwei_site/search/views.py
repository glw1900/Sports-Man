from django.http import HttpResponse
from django.template import RequestContext
from ElasticSearch.Esearch import ES_query
from django.shortcuts import render
from .models import State

def index(request):
    # context = RequestContext(request)
    states = State.objects.all()
    # to_search = request.Get.get("Court_Name")
    # q = ES_query()
    # hits = q.q_place(to_search)


    return render(request,'search/index.html',{'states':states})


def search_result(request):
    if 'Court_Name' in request.POST:
        to_search = request.POST['Court_Name']
        q = ES_query()
        hits = q.q_place(to_search)
        output = []
        for i in range(min(10,len(hits))):
            temp = 'rank: ' + str(i+1)
            stadium = hits[i]["_source"]
            temp = temp + '     name: ' + stadium['name'][0]
            output.append(temp)
        return render(request,'search/search_result.html',{'hits':hits,'output':output})
    else:
        return HttpResponse("Nothing found");

