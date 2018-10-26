from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb
import re
from myScrapy.utils.helpers import format_str
'''
一呼百应
'''

class YhbySpider(Spider):
    name = 'yhbyspider'
    
    def __init__(self, *args, **kwargs):
        self.count = rdb.get('yhby_page')
        if not self.count:
            self.count = 1
        else:
            self.count = int(self.count.decode())
        super(YhbySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        self.log('start request start:**********************', self.count)
        start = self.count
        if start == 99:
            hrefs = [href.decode() for href in rdb.lrange('yhby_urls', 0, -1)]
            for href in hrefs:
                yield Request(href, self.parseCompany, dont_filter=True)
        else:
            for i in range(start, 100):
                self.count = i
                url = 'http://www.youboy.com/scom?kw=&p={}'.format(i)
                yield Request(url, self.parse, dont_filter=True)
    
    def parse(self, response):
        for query in response.css('div.searchPdListCon div.searchPdListConL div.gysItemsWrap'):
            href = query.xpath('./div[@class="gysItems"]/div[@class="gysItemsL"]/a/@href').extract_first()
            rdb.rpush('yhby_urls', href+'contact.html')
        rdb.set('yhby_page', self.count)
        if self.count == 99:
            hrefs = [href.decode() for href in rdb.lrange('yhby_urls', 0, -1)]
            for href in hrefs:
                yield Request(href, self.parseCompany, dont_filter=True)        
    
    def parseCompany(self, response):
        card = response.css('div.contactCard')
        item = CompanyInfoItem()
        if card:
            cardtab = response.xpath('./table/tbody')
            name = cardtab.xpath('./tr/td[contains(text(), "公司名")]/../td[2]/text()').extract_first()
            address = cardtab.xpath('./tr/td[contains(text(), "公司地址")]/../td[2]/i/text()').extract_first()
            if not address:
                address = cardtab.xpath('./tr/td[contains(text(), "公司地址")]/../td[2]/text()').extract_first()
            contact = cardtab.xpath('./tr/td[contains(text(), "联系人")]/../td[2]/text()').extract_first()
            mobile = cardtab.xpath('./tr/td[contains(text(), "手机号码")]/../td[4]/text()').extract_first()
            if mobile:
                mobile = re.findall("\d+", mobile)[0]
            tel = cardtab.xpath('./tr/td[contains(text(), "电话号码")]/../td[4]/text()').extract_first()
            if tel:
                tel = re.findall("\d+", tel)[0]
        else:
            query = response.xpath('//div[@class="lianxi_wrap"]')
            name = query.xpath('./div[2]/p/font/text()').extract_first()
            address = query.xpath('./div[2]/p[2]/i/text()').extract_first()
            contact = query.xpath('./div[3]/ul/li/font[contains(text(), "联系人")]/../text()').extract()
            try:
                contact = format_str(contact[1])
            except:
                contact = ''
            mobile = query.xpath('./div[3]/ul/li/font[contains(text(), "手机")]/../text()').extract()
            try:
                mobile = format_str(mobile[1])
            except:
                mobile = ''
            tel = ''
        item['name'] = name
        item['address'] = address
        item['tel'] = tel
        item['mobile'] = mobile
        item['contact'] = contact
        item['meta'] = 'yihubaiying'
        item['url'] = response.url
        yield item