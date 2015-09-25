

from pyparsing import *
from googleplaces import GooglePlaces

YOUR_API_KEY = 'AIzaSyCTqay66rwdaS5CdL9C2BArgrh5Xxwprfs'

google_places = GooglePlaces(YOUR_API_KEY)

def map_sports(sports):
    filtered=filter(lambda x: not x in {'area','place','places','location','resort','court','courts'},sports)
    sport='_'.join(filtered).lower()
    map={'snowboard':'ski','snowboarding':'ski','swimming_pool':'swim','swimming_pools':'swim','swimming':'swim'}
       
    if sport in ['ski','swim','tennis','rock_climbing','badminton']:
        return sport
    elif sport in map:
        return map[sport]

    return ''

def map_attributes(sport,attributes):
    attr_mapping={'swim':{},'tennis':{'courts':'num_courts'}}
    attr='_'.join(attributes)
    if attr_mapping.has_key(sport):
        striped=attr.replace('number_of_','')
        if attr_mapping[sport].has_key(striped):
            return attr_mapping[sport][striped]
        elif attr_mapping[sport].has_key(attr):
            return attr_mapping[sport][attr]
        else:
            return striped
    else:
        return attr

def unit_normalize(qattribute,unit):
    swim_unit={'meter':'m','meters':'m','yards':'y','yd':'y'}
    normalize_dict={'swim.length':swim_unit,'swim.width':swim_unit}
    if qattribute in normalize_dict and unit in normalize_dict[qattribute]:
        return normalize_dict[qattribute][unit]
    return unit
def default_query(string):
    return {"query" :{"multi_match":{
    "query":    string, 
    "fields": [ "address", "name", "summary" ] 
  }}}

# populate ingredients->recipes "database"

# classes to be constructed at parse time, from intermediate ParseResults
class UnaryOperation(object):
    def __init__(self, t):
        self.op, self.a = t[0]
class BinaryOperation(object):
    def __init__(self, t):
        self.op = t[0][1]
        self.operands = t[0][0::2]
class SearchAnd(BinaryOperation):
    def gen_query(self,sport):
        return {
            "and" : [oper.gen_query(sport) for oper in self.operands]
        }
    def __repr__(self):
        return "AND:(%s)" % (",".join(str(oper) for oper in self.operands))
class SearchOr(BinaryOperation):
    def gen_query(self,sport):
        return {
            "or" : [oper.gen_query(sport) for oper in self.operands]
        }
    def __repr__(self):
        return "OR:(%s)" % (",".join(str(oper) for oper in self.operands))
class SearchNot(UnaryOperation):
    def gen_query(self,sport):
        return {
            "not" : self.a.gen_query(sport)
        }
    def __repr__(self):
        return "NOT:(%s)" % str(self.a)
class SearchTerm(object):
    def __init__(self, tokens):
        self.term = tokens[0]
    def generateSetExpression(self):
        if self.term in recipesByIngredient:
            return "set(recipesByIngredient['%s'])" % self.term
        else:
            return "set()"
    def __repr__(self):
        return self.term

class CondExpr(object):
    def __init__(self, t):
        self.term = t[0].term
        self.op = ' '.join(t[0].op)
        self.value = t[0].valueexpr.value
        self.unit=t[0].valueexpr.unit

    def gen_query(self,sport):
        op_dict={'greater than':'gt','more than':'gt','>':'gt','less than':'lt','<':'lt','>=':'gte','<=':'lte'}
        term=sport + '.' +map_attributes(sport,self.term)
        unit=unit_normalize(term,self.unit)
        value = str(self.value) + unit if unit else self.value
        if self.op=='=':
            return {
            "term" : { term : value}
        }
        else:
           esop=op_dict[self.op]
           return {
            "range" : {
                term : {
                    esop: value
                }
            }
        }
    def __repr__(self):
        return self.term

class QueryString():
    def __init__(self, t):
        self.sports = t.sports
        self.inexpr = t.inexpr
        self.withexpr = t.withexpr
        self.rangeexpr= t.rangeexpr
        self.geolocation = (42.3688784,-71.2467742)
        

    def get_current_location(self):
        return self.geolocation

    def query_location(self,qs):
        query_result = google_places.text_search(query=qs)
        if len(query_result.places) == 0:
            return self.get_current_location()
        else:
            place=query_result.places[0]
            return (place.geo_location['lat'],place.geo_location['lng'])


    def gen_range_expr(self):
        key,expr = self.rangeexpr[0],self.rangeexpr[1:]
        distance = '10miles'
        origin = 'me'
        
        if key == 'within':
            distance = str(expr[0]) + expr[1]
            if 'fromloc' in self.rangeexpr:
                origin=' '.join(self.rangeexpr['fromloc'])
        elif key == 'near':
            origin = (' '.join(expr)).strip()
        if origin == 'me':
            origin=self.get_current_location()
        else:
            origin=self.query_location(origin)
        return ({
            "geo_distance" : {
                "distance" : distance,
                "geo_location" : {
                    "lat" : origin[0],
                    "lon" : origin[1]
                }
            }
        },{
      "_geo_distance": {
        "geo_location": { 
          "lat":  origin[0],
          "lon": origin[1]
        },
        "order":         "dsc",
        "unit":          "km", 
        "distance_type": "plane" 
      }
    })
  

    def gen_in_expr(self):

        return {"match": {"address": {"query":' '.join(self.inexpr[1:]), "operator": "and"}}}

    def gen_with_expr(self,sport):
        return self.withexpr[1].gen_query(sport)


    def gen_query(self,geolocation):
        self.geolocation=geolocation
        filter = self.rangeexpr or self.withexpr
        sport=map_sports(self.sports)
        queries=[]
        sort = None
        if sport:
            queries.append({"match": {"activity_types": sport}})
        else:
            raise ValueError('unsupported sports')
        filters=[]
        if self.inexpr:
            queries.append(self.gen_in_expr())
        if self.rangeexpr:
            query,sort=self.gen_range_expr()
            filters.append(query)
        if self.withexpr:
            filters.append(self.gen_with_expr(sport))
        query ={}
        queries = {"bool" : {"must": queries}} if len(queries) > 1 else queries[0]
        
        if filter:
            filters = {"bool" : {"must": filters}} if len(filters) > 1 else filters[0]
            query['query'] = {
    "filtered" : {
        #"query" : {"bool" : {"must": queries}} if len(queries) > 1 else queries[0],
        "query" : queries,
        "filter" : filters
    }
}
        else:
            query['query']=queries
        if sort:
            query["sort"] =[sort]
        print query
        return query

# define the grammar
class NLQuery(object):
    def __init__(self):
        and_ = CaselessLiteral("and")
        or_ = CaselessLiteral("or")
        not_ = CaselessLiteral("not")
        lookahead=oneOf("in with within near")
        locationExpr = OneOrMore(~lookahead + Word(srange("[a-zA-Z_0-9]")) | ',')
        sportsExpr = Group(OneOrMore(~lookahead + Word(srange("[a-zA-Z]"))))
        nearExpr = Group(CaselessKeyword("near") + (CaselessKeyword("me") | locationExpr))
        inExpr = CaselessKeyword("in") + locationExpr

        number_ = Word(nums).addParseAction(lambda t: int(t[0]))
        units = oneOf("km m mile miles ac ft feet yard yards y kilometers kilometer meter meters")
        valueExpr = number_('value') + Optional(units)('unit')
        
        withinExpr = Group(CaselessKeyword("within") + valueExpr + Optional(CaselessKeyword('from').suppress() + locationExpr('fromloc')))
        #withinExpr.setParseAction(WithinExpr)
        tlookahead=oneOf("in with within near < > >= <= = more and or not more less greater")
        searchTerm = Group(OneOrMore(~tlookahead + Word(srange("[a-zA-Z]"))) | quotedString.setParseAction( removeQuotes ))
        #searchTerm.setParseAction(SearchTerm)
        condExpr = Group(searchTerm('term') + Group(oneOf('< > >= <= =') | oneOf('more less greater') + 'than' )('op')  + valueExpr('valueexpr') | (oneOf('more less greater') + 'than')('op') +  valueExpr('valueexpr') + searchTerm('term') )
        condExpr.setParseAction(CondExpr)
        searchExpr = operatorPrecedence( condExpr,
         [
         (not_, 1, opAssoc.RIGHT, SearchNot),
         (and_, 2, opAssoc.LEFT, SearchAnd),
         (or_, 2, opAssoc.LEFT, SearchOr),
         ])
        withExpr = CaselessKeyword("with") + searchExpr
        queryString = sportsExpr('sports') + Optional(inExpr)('inexpr') + Optional(withExpr)('withexpr') + Optional(withinExpr | nearExpr)('rangeexpr')
        queryString.addParseAction(QueryString)
        self.query_str=queryString

    def gen_query(self,string,geolocation):
        try:
            evalStack = (self.query_str + stringEnd).parseString(string)
            return evalStack[0].gen_query(geolocation)
        except Exception, pe:
            print pe
            return default_query(string)

if __name__ == "__main__":
# test the grammar and selection logic
    test = """snowboard places in Vermount with more than 100 trails
     swimming pools with number of lanes > 5 and length = 25m within 10km from Boston
     ski resorts within 20miles
     tennis court near Waltham, MA
     ski places near me
     ski places in MA""".splitlines()
    nlquery=NLQuery()
    for t in test:
     print "Search string:", t
     print "Eval stack: ", nlquery.gen_query(t,(1,2))
     #evalExpr = evalStack.generateSetExpression()
    # print "Eval expr: ", evalExpr