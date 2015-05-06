from scrapy import Spider, Item, Field

import scrapy

class TennisCourtItem(Item):
    name = Field()
    address = Field()
    tel = Field()
    num_courts = Field()
    type = Field()
    court_lighted = Field()
    court_indoor = Field()

class TennisCourtSpider(Spider):
    name = 'tennis_courts'
    allowed_domains = ['tennisround.com']
    start_urls =  ['http://www.tennisround.com/tennis-courts/']

    #def __init__(self):
    #    self.cities = {}
    #    self.result = {'courts':{}}
    #    self.id_counter = 0

    #def read_cities(self):
    #    fo = open("cities.json", 'r')
    #    self.cities = json.loads(fo.read())
    #    fo.close()

    def parse(self,response):
        #self.read_cities()
        #for city in self.cities['cities']:
         #   yield scrapy.Request('http://www.tennisround.com/tennis-courts/' + city, self.parse)
        for link in response.css('.span8 > table a'):
            url = "http://www.tennisround.com" + link.xpath('@href').extract()[0]
            yield scrapy.Request(url,callback=self.godown)

    def godown(self,response):
        for link in response.css('.span8 > table a'):
            url = "http://www.tennisround.com" + link.xpath('@href').extract()[0]
            yield scrapy.Request(url,callback=self.strip)

    def strip(self, response):
        for court in response.xpath('//div[@class="span4 court-info"]'):
            item=TennisCourtItem()
            item['name'] = court.xpath("//div[@class='name']//a/text()").extract()
            item['address'] = court.xpath("//span[@class='label label-success']/preceding-sibling::text()").extract()
            item['tel'] = court.xpath("//span[@class='label label-success']/following-sibling::text()").extract()
            item['type'] = court.xpath("//span[@class='label label-success']/text()").extract()
            item['num_courts'] = court.xpath("//div[@class='court-total']/text()").extract()
            item['court_lighted'] = court.xpath("//div[@class='court-lighted']/text()").extract()
            item['court_indoor'] = court.xpath("//div[@class='court-indoor']/text()").extract()
            yield item
        #court_list = [Post(court=courts[i].extract(), address=addresses[i*3].extract().strip(), tel=addresses[i*3+2].extract().strip(), num_courts=num_courts[i].extract().strip()) for i in xrange(0, len(courts))]
       # for i in xrange(0, len(courts)):
	   #     self.result['courts'][str(self.id_counter + 1)] = dict(Post(court=courts[i].extract(), address=addresses[i*3].extract().strip(), tel=addresses[i*3+2].extract().strip(), num_courts=num_courts[i].extract().strip()))
	    #    self.id_counter += 1
        #self.result['courts'] += court_list
        #self.result['courts'] = json.dumps(self.result['courts'])
        #self.write_json(self.result)
       # return self.result['courts'][str(self.id_counter)]


