from googleplaces import GooglePlaces, types, lang
import json
import io
import sys, codecs
import re
# set up output encoding
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

YOUR_API_KEY = 'AIzaSyCTqay66rwdaS5CdL9C2BArgrh5Xxwprfs'
    #'AIzaSyDWvbupdPsaDcbzBsEjc7El5QYDu6eregc'
    #'AIzaSyAROXFHSbtR0OA1hNKP8VaBRaUzUegksPA'

google_places = GooglePlaces(YOUR_API_KEY)

def add_google_places(placeiter,output,term,process_func,usegoogle=False):
    places = []
    print len(placeiter)
    i=0
    for elem in placeiter:

        #if query_result.has_attributions:
         #   print query_result.html_attributions
        #print query_result
        result={}
        if usegoogle:
            query_result = google_places.text_search(
            query= elem[term])
            if len(query_result.places) == 0 and elem.has_key('address'):
                query_result = google_places.text_search(query= elem['address'])
        
            result['name']=elem[term]
            print elem[term]
            if len(query_result.places) == 0:
                print 'Error: Google Return no results'
            else:
                place=query_result.places[0]
                try:
                    place.get_details()
                    result['address']=place.formatted_address
                    result['international_phone_number']=place.international_phone_number
                    result['local_phone_number']=place.local_phone_number
                    if place.website:
                        result['website']=place.website
                    result['google_url']=place.url
                    result['google_maps_id']=place.place_id
                except:
                    pass
            
                result['geo_location']={'lat':place.geo_location['lat'],'lon':place.geo_location['lng']}
            

        process_func(elem,result)
        
        places.append(result)
        if (i+1) % 5000 == 0:
            print i+1
            with io.open(output,'wb')  as f:
                jsonfile=json.dumps(places, sort_keys=True, indent=4)
                f.write(jsonfile)
        i += 1
        #print result

    with io.open(output,'wb')  as f:
        jsonfile=json.dumps(places, sort_keys=True, indent=4)
        f.write(jsonfile)

def process_google(placeiter,output):
    places = []
    print len(placeiter)
    for elem in placeiter:
        result={}
        result['name']=elem['name']
        result['address']=elem['formatted_address']
        if elem.has_key('international_phone_number'):
            result['international_phone_number']=elem['international_phone_number']
        if elem.has_key('formatted_phone_number'):
            result['local_phone_number']=elem['formatted_phone_number']
        if elem.has_key('website'):
            result['website']=elem['website']
        result['google_url']=elem['url']
        result['google_maps_id']=elem['place_id']
        result['geo_location']={'lat':elem['geometry']['location']['lat'],'lon':elem['geometry']['location']['lng']}
        places.append(result)
    with io.open(output,'wb')  as f:
        jsonfile=json.dumps(places, sort_keys=True, indent=4)
        f.write(jsonfile)


def process_ski(elem,result):
    result['activity_types']=['ski','snowboard']
    specialized={}
    for attr in ["fast_eight", "beginner", "trails", "fast_sixes", "surface", "triple", "quad", "expert", "fast_quads", "longest_run", "trams", "lifts", "terrain_parks", "intermediate", "advanced", "double"]:
        if not elem.has_key(attr) or elem[attr] == '':
            continue
        #print attr,elem[attr]
        specialized[attr]=int(elem[attr])

    for attr in ["drop", "summit", "base","skiable_area", "snow_making"]:
        if not elem.has_key(attr) or elem[attr] == '':
            continue
        #print attr,elem[attr]
        specialized[attr]=elem[attr]

    result['ski'] = specialized

def process_tennis(elem,result):
    result['activity_types']='tennis'
    specialized={}
    for attr in ["num_courts"]:
        if not elem.has_key(attr) or elem[attr] == '-':
            continue
        #print attr,elem[attr]
        specialized[attr]=int(elem[attr])
    result['name']=elem['court']
    result['address'] = elem['address']
    result['international_phone_number']=elem['tel'].replace('Phone ','+1 ')
    result['local_phone_number']=re.sub(r'^(\d{3})-',r'(\1) ',elem['tel'].replace('Phone ',''))
    result['tennis'] = specialized

def process_swimming(elem,result):
    result['activity_types']='swim'
    specialized={}
    for pool in elem["pools"]:
        i=0
        for attr in pool.split(','):
            i+=1
            attr=attr.strip()
            match=re.match('(\d+\w+)(?:\s*x\s*(\d+\w+))?',attr)
            if match and i==1:
                specialized['length']=match.group(1)
                if match.group(2):
                    specialized['width']=match.group(2)
                continue
            if re.match('indoors|outdoors',attr):
                specialized['type']=attr
                continue
            match=re.match('(\d+)\s+lanes',attr)
            if match:
                specialized['lanes']=int(match.group(1))
                continue
            match=re.match('(.+)\s+depth',attr)
            if match:
                specialized['depth']=match.group(1)
                continue

    for attr in ["name", "address", "website"]:
        if not elem.has_key(attr) or elem[attr] == '':
            continue
        result[attr]=elem[attr]
    for attr in ["notes", "reviews","pools","admission"]:
        if not elem.has_key(attr) or elem[attr] == '':
            continue
        specialized[attr]=elem[attr]
    result['local_phone_number']=elem['tel']
    
    try:
        latlng=elem['latlong'][0].split(',')
        lat=float(latlng[0])
        lng=float(latlng[1])
        result['geo_location']={'lat':lat,'lon':lng}
    except:
        print elem['name']
    result['swim'] = specialized

if __name__ == '__main__':
    #skiplaces=json.load(open(r'data\onthesnow.json','r'))
    #add_google_places(skiplaces,r'data\onthesnowplace.json','name',process_ski)
    #tenniscorts=json.load(open(r'google_swimming.txt','r'))
    #process_google(tenniscorts.values(),r'data\google_swiming.json')
    skiplaces=json.load(open(r'data\swimmersguide.json','r'))
    add_google_places(skiplaces,r'data\swimmersguide_google.json','name',process_swimming,False)