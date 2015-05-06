__author__ = 'guoliangwei'

import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

class rock_climbing_item(scrapy.Item):
    name = scrapy.Field()
    location = scrapy.Field()
    phone_number = scrapy.Field()
    offcial_website = scrapy.Field()
    description = scrapy.Field()

class rock_climbing_spider(scrapy.Spider):

    name = "rock_climbing"
    allowed_domains = ["indoorclimbing.com"]
    start_urls = [
        'http://www.indoorclimbing.com/worldgyms.html'
    ]

    def parse(self, response):
        
        for link in response.css('div.indexcolumns > table a'):
            url = "http://www.indoorclimbing.com/" + link.xpath('@href').extract()[0]
            yield scrapy.Request(url,callback=self.strip)
    def strip(self,response):
        for q in response.xpath('//*[@id="print"]/ol/li'):
                item = rock_climbing_item()
                item['name'] = q.xpath('b/text()').extract()[0]
                list=q.xpath('span[@class="red"]/preceding-sibling::text()').extract()
                if len(list) > 2:
                    item['location'] = list[0:2]
                if len(list)>=3:
                    item['phone_number'] = list[2]
                list=q.xpath('span[@class="red"]/following-sibling::text()').extract()
                if len(list)>0:
                    item['description']=list[0]
                item['offcial_website'] = q.xpath('a/@href').extract()
                yield item











