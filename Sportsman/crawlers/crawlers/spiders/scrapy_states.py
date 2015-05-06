#So far just for this tennis website.


from scrapy import Spider, Item, Field

import json

class Post(Item):
	state = Field()

class TennisStateSpider(Spider):
	name, start_urls = 'tennis_states', ['http://www.tennisround.com/tennis-courts/']

	def parse(self, response):
		states = response.xpath("//a[contains(., 'ennis courts in')]//@href")
		result = [Post(state=state.extract().replace('/tennis-courts/', ''))['state'] for state in states]
		self.write_json({'states': result})
		return result

	def write_json(self, result_dict):
		"""write dictionary to json file"""
		states_data = open('states.json', 'w')
		states_data.write(json.dumps(result_dict, indent = 4, sort_keys = True))
		states_data.close()
