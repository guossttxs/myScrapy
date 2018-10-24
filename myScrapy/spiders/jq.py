from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb
from myScrapy.utils.mongo import MongoObj
from myScrapy.utils.helpers import format_str

'''
金泉网
'''

class JQSpider(Spider):
    name = 'jqspider'

    def __init__(self, *args, **kwargs):
        curPage = int(rdb.get('jqw_cur_page').decode()) if rdb.get('jqw_cur_page') else 0
        maxPage = int(rdb.get('jqw_pages').decode()) if rdb.get('jqw_pages') else 10000
        self.curPage = curPage
        self.maxPage = 500
        self.cityCode = [1, 129, 350, 371, 453, 573, 686, 840, 973, 1095, 1138, 1170, 1223, 1245, 1409, 1551, 1726, 1866, 1887, 1991, 2104, 2242, 2346, 2393, 2588, 2782, 2941, 3091, 3169, 3302, 3431, 3554, 3973, 4002]
        super(JQSpider, self).__init__(*args, **kwargs)
    
    def start_requests(self):
        # for code in self.cityCode:
        #     self.curPage = 0
        #     while self.curPage <= self.maxPage:
        #         self.curPage += 1
        #         url = 'http://www.product.jqw.com/a{}/{}/plist.html'.format(code, self.curPage)
        #         yield Request(url, self.parse, dont_filter=True)
        mongo = MongoObj()
        db = mongo.get_db()
        datas = db.companys.find({'meta': 'jqw', 'contact': ''}, {'url': 1})
        urls = [data.get('url') for data in datas]
        for url in urls:
            yield Request(url, self.parseCompany, dont_filter=True)
    
    def parse(self, response):
        rdb.set('jqw_cur_page', self.curPage)
        maxPage = response.xpath('//div[@class="searchPage"]/span/strong/text()').extract_first()
        self.maxPage = int(maxPage) if maxPage else self.maxPage
        for l in response.xpath('//div[@class="company"]/ul[@id="dataList"]/li'):
            href = l.xpath('./div/a/@href').extract_first()
            #yield Request(href, self.parseCompany, dont_filter=True)
            data = l.xpath('./div/div')
            company = data.xpath('./div/p[contains(text(), "公司")]/../p[2]/a/text()').extract_first()
            tel = data.xpath('./div/p[contains(text(), "电话")]/../p[2]/text()').extract_first()
            address = data.xpath('./div/p[contains(text(), "地址")]/../p[2]/text()').extract_first()
            item = CompanyInfoItem()
            tel_sp = tel.split('|')
            for tel in tel_sp:
                if tel:
                    item['name'] = company
                    item['contact'] = ''
                    item['tel'] = tel
                    item['address'] = address
                    item['url'] = href
                    item['meta'] = 'jqw'
                    yield item
        
    def parseCompany(self, response):
        item = CompanyInfoItem()
        query = response.xpath('//div[@alt="jqwlx"]/ul/li')
        company = query.xpath('./p[contains(text(), "企业")]/../p[2]/span/a/text()').extract_first()
        contact = query.xpath('./p[contains(text(), "联系")]/../p[2]/span/text()').extract_first()
        tel = query.xpath('./p[contains(text(), "手机")]/../p[2]/span/text()').extract_first()
        #mobile = query.xpath('./p[contains(text(), "手机")]/../p[2]/span/text()').extract_first()
        address = query.xpath('./p[contains(text(), "地址")]/../p[2]/span/text()').extract_first()
        
        item['name'] = company
        item['contact'] = contact
        item['tel'] = format_str(tel)
        item['address'] = address
        item['url'] = response.url
        item['meta'] = 'jqw'
        yield item

        tel2 = query.xpath('./p[contains(text(), "手机")]/../following-sibling::li[1]/p[2]/span/text()').extract_first()
        tel2 = format_str(tel2)
        if tel2:
            item['tel'] = tel2
            yield item