#So far just for this tennis website.


from scrapy import Spider, Item, Field

import json
import scrapy

class Post(Item):
	court = Field()
	address = Field()
	tel = Field()
	num_courts = Field()
	type = Field()
	lighted = Field()
	indoor = Field()

class TennisCourtSpider(Spider):
	name = 'tennis_courts'
	allowed_domains = ['tennis_courts']
	#name, start_urls = 'tennis_states', ['http://www.tennisround.com/tennis-courts/' + state]

	def __init__(self):
		self.cities = {}
		self.result = {'courts':{}}
		self.id_counter = 0

	def read_cities(self):
		fo = open("cities.json", 'r')
		self.cities = json.loads(fo.read())
		fo.close()

	def start_requests(self):
		self.read_cities()
		for city in self.cities['cities']:
			yield scrapy.Request('http://www.tennisround.com/tennis-courts/' + city, self.parse)

	def parse(self, response):
		courts = response.xpath("//div[@class='name']//a/text()")
		addresses = response.xpath("//div[@class='court-address']/text()")
		num_courts = response.xpath("//div[@class='court-total']/text()")
		#court_list = [Post(court=courts[i].extract(), address=addresses[i*3].extract().strip(), tel=addresses[i*3+2].extract().strip(), num_courts=num_courts[i].extract().strip()) for i in xrange(0, len(courts))]
		for i in xrange(0, len(courts)):
			self.result['courts'][str(self.id_counter + 1)] = dict(Post(court=courts[i].extract(), address=addresses[i*3].extract().strip(), tel=addresses[i*3+2].extract().strip(), num_courts=num_courts[i].extract().strip()))
			self.id_counter += 1
		#self.result['courts'] += court_list
		#self.result['courts'] = json.dumps(self.result['courts'])
		self.write_json(self.result)
		return self.result['courts'][str(self.id_counter)]

	def write_json(self, result_dict):
		"""write dictionary to json file"""
		courts_data = open('tennis_courts.json', 'w')
		courts_data.write(json.dumps(result_dict, indent = 4, sort_keys = False))
		courts_data.close()

