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


def add_google_places(placeiter,output,term,process_func):
    places = []
    print len(placeiter)
    i=0
    for elem in placeiter:
        query_result = google_places.text_search(
        query= elem[term])
        if len(query_result.places) == 0 and elem.has_key('address'):
            query_result = google_places.text_search(query= elem['address'])
        
        #if query_result.has_attributions:
         #   print query_result.html_attributions
        #print query_result
        result={}
        result['name']=elem[term]
        print elem[term]
        if len(query_result.places) == 0:
            print 'Error: Google Return no results'
        else:
            place=query_result.places[0]
            place.get_details()
            
            result['address']=place.formatted_address
            result['international_phone_number']=place.international_phone_number
            result['local_phone_number']=place.local_phone_number
            if place.website:
                result['website']=place.website
            result['geo_location']={'lat':place.geo_location['lat'],'lon':place.geo_location['lng']}
            result['google_url']=place.url
            result['google_maps_id']=place.place_id

        process_func(elem,result)
        
        places.append(result)
        if (i+1) % 100 == 0:
            with io.open(output,'wb')  as f:
                jsonfile=json.dumps(places, sort_keys=True, indent=4)
                f.write(jsonfile)
        i += 1
        #print result

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

if __name__ == '__main__':
    #skiplaces=json.load(open(r'data\onthesnow.json','r'))
    #add_google_places(skiplaces,r'data\onthesnowplace.json','name',process_ski)
    tenniscorts=json.load(open(r'tennis_courts.json','r'))
    add_google_places(tenniscorts["courts"].values(),r'data\tenniscourtsplace.json','court',process_tennis)