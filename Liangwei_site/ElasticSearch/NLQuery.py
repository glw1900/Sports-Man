

from pyparsing import *
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
        self.value = t[0].value

    def gen_query(self,sport):
        op_dict={'more than':'gt','>':'gt','less than':'lt','<':'lt','>=':'gte','<=':'lte'}
        term=sport + '.' +self.term
        if self.op=='=':
            return {
            "term" : { term : self.value}
        }
        else:
           esop=op_dict[self.op]
           return {
            "range" : {
                term : {
                    esop: self.value
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

    def get_current_location(self):
        return (42.3688784,-71.2467742)

    def query_location(self,qs):
        return (1,2)

    def gen_range_expr(self):
        key,expr = self.rangeexpr[0],self.rangeexpr[1:]
        distance = '10miles'
        origin = 'me'
        if key == 'within':
            distance = expr[0] + expr[1]
        elif key == 'near':
            origin = expr
        if origin == 'me':
            origin=self.get_current_location()
        else:
            origin=self.query_location(origin)
        return {
            "geo_distance" : {
                "distance" : distance,
                "geo_location" : {
                    "lat" : origin[0],
                    "lon" : origin[1]
                }
            }
        }

    def gen_in_expr(self):

        return {"match": {"address": {"query":' '.join(self.inexpr[1:]), "operator": "and"}}}

    def gen_with_expr(self,sport):
        return self.withexpr[1].gen_query(sport)

    def map_sports(self,sports):
        return 'ski'
    def gen_query(self):
        filter = self.rangeexpr or self.withexpr
        sport=self.map_sports(self.sports)
        queries=[{"match": {"activity_types": sport}}]
        filters=[]
        if self.inexpr:
            queries.append(self.gen_in_expr())
        if self.rangeexpr:
            filters.append(self.gen_range_expr())
        if self.withexpr:
            filters.append(self.gen_with_expr(sport))
        query ={}
        queries = {"bool" : {"must": queries}} if len(queries) > 1 else queries[0]
        filters = {"bool" : {"must": filters}} if len(filters) > 1 else filters[0]
        if filter:
            query['query'] = {
    "filtered" : {
        #"query" : {"bool" : {"must": queries}} if len(queries) > 1 else queries[0],
        "query" : queries,
        "filter" : filters
    }
}
        else:
            query['query']=queries
        print query
        return query

# define the grammar
class NLQuery(object):
    def __init__(self):
        and_ = CaselessLiteral("and")
        or_ = CaselessLiteral("or")
        not_ = CaselessLiteral("not")
        lookahead=oneOf("in with within near")
        locationExpr = OneOrMore(Word(alphas) | ',')
        sportsExpr = Group(OneOrMore(~lookahead + Word(alphas)))
        nearExpr = Group(CaselessKeyword("near") + (CaselessKeyword("me") | locationExpr))
        inExpr = CaselessKeyword("in") + locationExpr

        number_ = Word(nums).addParseAction(lambda t: int(t[0]))
        units = oneOf("km m mile miles ac")
        valueExpr = Word(nums) + Optional(units)
        withinExpr = Group(CaselessKeyword("within") + valueExpr)
        #withinExpr.setParseAction(WithinExpr)
        searchTerm = Word(alphas) | quotedString.setParseAction( removeQuotes )
        #searchTerm.setParseAction(SearchTerm)
        condExpr = Group(searchTerm('term') + Group(oneOf('< > >= <= =') | oneOf('more less') + 'than' )('op')  + number_('value') | (oneOf('more less') + 'than')('op') + number_('value') + searchTerm('term') )
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

    def gen_query(self,string):
        try:
            evalStack = (self.query_str + stringEnd).parseString(string)
            return evalStack[0].gen_query()
        except ParseException, pe:
            return "Invalid search string"

if __name__ == "__main__":
# test the grammar and selection logic
    test = """\
     ski places with more than 100 trails and skiableareas > 3500
     ski resorts within 20miles
     ski areas near Waltham, MA
     ski places near me
     ski places in MA""".splitlines()
    nlquery=NLQuery()
    for t in test:
     print "Search string:", t
     print "Eval stack: ", nlquery.gen_query(t)
     #evalExpr = evalStack.generateSetExpression()
    # print "Eval expr: ", evalExpr