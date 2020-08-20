from scrapy import Spider, Request
from yelp.items import YelpItem 
import re

class YelpSpider(Spider):
    name = 'yelp_spider'
    allowed_urls = ['https://www.yelp.com']
    start_urls = ['https://www.yelp.com/search?find_desc=Coffee%20Shop&find_loc=Midtown%20West%2C%20Manhattan%2C%20NY&start=0']

    def parse(self, response):
        num_pages = response.xpath('//div[@class="lemon--div__373c0__1mboc border-color--default__373c0__3-ifU text-align--center__373c0__2n2yQ"]/span/text()').extract_first()
        num_pages = int(re.findall('1 of (\d+)', num_pages)[0])

        url_list = [f'https://www.yelp.com/search?find_desc=Coffee%20Shop&find_loc=Midtown%20West%2C%20Manhattan%2C%20NY&start={i*30}' for i in range(num_pages)]


        for url in url_list:
            yield Request(url=url, callback=self.parse_results_page)

    def parse_results_page(self, response):
        business_urls = response.xpath('//div//h4//a[@class="lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE"]/@href').extract()
        business_urls = business_urls[2:-1]
        business_urls = [f'https://www.yelp.com{business}' for business in business_urls]

        for url in business_urls:
            yield Request(url=url, callback=self.parse_business_page)

    def parse_business_page(self, response):
        business_name = response.xpath('//h1[@class="lemon--h1__373c0__2ZHSL heading--h1__373c0__dvYgw undefined heading--inline__373c0__10ozy"]/text()').extract_first()
        fulladdress = response.xpath('//address[@class="lemon--address__373c0__2sPac"]//span/text()').extract()
        address = ', '.join(fulladdress)
        zipcode = response.xpath('//address[@class="lemon--address__373c0__2sPac"]//span/text()').extract()[1].split(' ')[-1]

        days = response.xpath('//table[@class="lemon--table__373c0__2clZZ hours-table__373c0__1S9Q_ table__373c0__3JVzr table--simple__373c0__3lyDA"]//tr')
        hours_dict = {day.xpath('./th/p/text()').extract_first():day.xpath('./td/ul/li/p/text()').extract_first() for day in days}

        item = YelpItem()
        item['business_name'] = business_name
        item['address'] = address
        item['zipcode'] = zipcode
        item['business_hours'] = hours_dict

        yield item

