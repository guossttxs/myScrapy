from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb

'''
大众点评
'''

class DzdpSpider(Spider):
    name = 'dzdp'

    def start_requests(self):
        citys = rdb.lrange('dzdp_citys', 0, -1)
        if citys:
            for city in citys:
                pass
        else:
            url = 'http://www.dianping.com/citylist'
            yield Request(url, callback=self.parseCitys, dont_filter=True)
    
    def parseCitys(self, response):
        '''
        获取城市列表的URL，并存到redis
        '''
        for city in response.xpath('//div[class="main-citylist"]/div[class="findHeight"]/a/'):
            pass
