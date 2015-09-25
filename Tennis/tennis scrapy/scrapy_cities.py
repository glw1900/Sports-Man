#So far just for this tennis website.


from scrapy import Spider, Item, Field

import json
import scrapy

class Post(Item):
	city = Field()

class TennisStateSpider(Spider):
	name = 'tennis_cities'
	allowed_domains = ['tennis_cities']
	#name, start_urls = 'tennis_states', ['http://www.tennisround.com/tennis-courts/' + state]

	def __init__(self):
		self.states = {}
		self.result = {'cities':[]}

	def read_states(self):
		fo = open("states.json", 'r')
		self.states = json.loads(fo.read())
		fo.close()

	def start_requests(self):
		self.read_states()
		for state in self.states['states']:
			yield scrapy.Request('http://www.tennisround.com/tennis-courts/' + state, self.parse)

	def parse(self, response):
		cities = response.xpath("//a[contains(., 'ennis courts in')]//@href")
		city_list = [Post(city=city.extract().replace('/tennis-courts/', ''))['city'] for city in cities]
		self.result['cities'] += city_list
		self.write_json(self.result)
		return city_list

	def write_json(self, result_dict):
		"""write dictionary to json file"""
		cities_data = open('cities.json', 'w')
		cities_data.write(json.dumps(result_dict, indent = 4, sort_keys = False))
		cities_data.close()
