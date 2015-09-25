from ElasticSearch.Esearch import ES_query
from django.http import HttpResponse
from django.shortcuts import render
from .models import SportType
from search.toGolocation import to_golocation

def index(request):
    sportType = SportType.objects.all()
    lat = 0
    lng = 0
    if 'Court_Name' in request.POST:
        search_text = request.POST['Court_Name'];
    if 'Court_Name' in request.POST and 'selectedType' in request.POST:
        selectedType = request.POST['selectedType'].lower()
        if selectedType == 'swimming':
            selectedType = 'swim'
        elif selectedType == 'Badminton':
            selectedType = 'badminton'
        print selectedType
        to_search = request.POST['Court_Name']
        if to_search == '':
            geo = request.POST['geolocation'].encode()
            geolocation = geo.split(',')
            lat = float(geolocation[0].encode())
            lng = float(geolocation[1].encode())
        else:
            location = to_golocation(to_search)
            lat = location['lat']
            lng = location['lng']
        q = ES_query()
        hits = q.q_mwf(selectedType.lower(),lat,lng)
        output = []
        for i in range(min(10,len(hits['hits']['hits']))):
            res = hits['hits']['hits']
            temp = {}
            temp['rank'] = str(i+1)
            stadium = res[i]["_source"]
            temp['name'] = stadium['name']
            temp['phone'] = stadium['local_phone_number']
            temp['address'] = stadium['address']
            if 'website' in stadium:
                temp['website'] = stadium['website']
            if 'ski' in stadium:
                temp['description'] = stadium['ski']
            elif 'swim' in stadium:
                temp['description'] = stadium['swim']
            elif 'rock_climbing' in stadium:
                temp['description'] = stadium['rock_climbing']
            elif 'tennis' in stadium:
                temp['description'] = stadium['tennis']
            elif 'badminton' in stadium:
                temp['description'] = stadium['badminton']
            output.append(temp)
        return render(request,'search/index.html', {'sportType':sportType, 'selectedType':selectedType,'output':output, 'searchText': search_text})
    else:
        return render(request,'search/index.html', {'sportType':sportType})

def advanced_search(request):
    if 'query' in request.POST and 'location' in request.POST:
        query = request.POST['query']
        to_search = request.POST['location']
        if to_search == '':
            geo = request.POST['geolocation'].encode()
            geolocation = geo.split(',')
            lat = float(geolocation[0].encode())
            lng = float(geolocation[1].encode())
        else:
            location = to_golocation(to_search)
            lat = location['lat']
            lng = location['lng']
        q = ES_query()
        hits = q.q_nl(query,(lat,lng))
        output = []
        for i in range(min(10,len(hits['hits']['hits']))):
            res = hits['hits']['hits']
            temp = {}
            temp['rank'] = str(i+1)
            stadium = res[i]["_source"]
            temp['name'] = stadium['name']
            temp['phone'] = stadium['local_phone_number']
            temp['address'] = stadium['address']
            if 'website' in stadium:
                temp['website'] = stadium['website']
            if 'ski' in stadium:
                temp['description'] = stadium['ski']
            elif 'swim' in stadium:
                temp['description'] = stadium['swim']
            elif 'rock_climbing' in stadium:
                temp['description'] = stadium['rock_climbing']
            elif 'tennis' in stadium:
                temp['description'] = stadium['tennis']
            elif 'badminton' in stadium:
                temp['description'] = stadium['badminton']
            output.append(temp)

        return render(request,'search/advanced_search.html', {'output':output, 'queryText': query})
    else:
        return render(request,'search/advanced_search.html')