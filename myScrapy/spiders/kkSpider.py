from scrapy import Spider
from myScrapy.items import CompanyInfoItem

'''
Kk商务网
'''

class KKSpider(Spider):
    name = "kkspider"
    start_urls = ['http://cn.b2bkk.com/qiye/']

    def parse(self, response):
        self.log('获取地区企业名录地址')
        for href in response.css('.cityList a::attr(href)').re(r'http:\/\/cn.b2bkk.com\/qiye\/.*'):
            self.log(href)
            yield response.follow(href, self.parseCityCompanys, dont_filter=True)
    
    def parseCityCompanys(self, response):
        for company in response.xpath('//div[@class="com_lists"]/ul/li/a/@href').extract():
            yield response.follow(company, self.parseCompanyInfo, dont_filter=True)
    
    def parseCompanyInfo(self, response):
        def extract_with_css(query, reg=None):
            query = response.css(query)
            info = ''
            if query:
                if reg:
                    query = query.re(reg)
                    if query:
                        info = query[0]
                else:
                    info = query.extract_first()
            return info.strip()
            
        item = CompanyInfoItem()
        item['url'] = response.url
        item['mobile'] = extract_with_css('ul li::text', r'手机.*')
        item['tel'] = extract_with_css('ul li::text', r'电话.*')
        item['address'] = extract_with_css('ul li::text', r'地址.*')
        item['contact'] = extract_with_css('ul li::text', r'联系人.*')
        item['name'] = extract_with_css('div.head div h1::text')
        yield item
        