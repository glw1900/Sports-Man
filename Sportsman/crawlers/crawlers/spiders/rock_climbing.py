__author__ = 'guoliangwei'

import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

class rock_climbing_item(scrapy.Item):
    name = scrapy.Field()
    location = scrapy.Field()
    phone_number = scrapy.Field()
    offcial_website = scrapy.Field()

class rock_climbing_spider(scrapy.Spider):

    name = "rock_climbing"
    allowed_domains = ["indoorclimbing.com"]
    start_urls = [
        'http://www.indoorclimbing.com/massachusetts.html'
    ]

    def parse(self, response):
        for p in response.xpath('//*[@id="print"]/ol'):
            for q in p.xpath('li'):
                item = rock_climbing_item()
                item['name'] = q.xpath('b').extract()
                item['location'] = q.xpath('text()').extract()[0:2]
                item['phone_number'] = q.xpath('text()').extract()[2]
                item['offcial_website'] = q.xpath('a/@href').extract()
                yield item

        for link in response.xpath('//*[@id="mainmenu2"]/div[2]/p'):
            url = "http://www.indoorclimbing.com/" + link.xpath('a/@href').extract()[0]
            yield scrapy.Request(url,callback=self.parse)










