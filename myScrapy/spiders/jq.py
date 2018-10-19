from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb

'''
金泉网
'''

class JQSpider(Spider):
    name = 'jqspider'

    def __init__(self, *args, **kwargs):
        curPage = int(rdb.get('jqw_cur_page').decode()) if rdb.get('jqw_cur_page') else 0
        maxPage = int(rdb.get('jqw_pages').decode()) if rdb.get('jqw_pages') else 10000
        self.curPage = curPage
        self.maxPage = maxPage
        super(JQSpider, self).__init__(*args, **kwargs)
    
    def start_requests(self):
        while self.curPage <= self.maxPage:
            if self.curPage == 0:
                url = 'www.product.jqw.com/plist.html'
            else:
                url = 'www.product.jqw.com/{}/plist.html'.format(self.curPage)
            yield Request(url, self.parse, dont_filter=True)
    
    def parse(self, response):
        self.curPage += 1
        rdb.set('jqw_cur_page', self.curPage)
        maxPage = response.xpath('//div[@class="searchPage"]/span/strong/text()').extract_first()
        self.maxPage = int(maxPage) if maxPage else self.maxPage
        for l in response.xpath('//div[@class="company"]/ul[@id="dataList"]/li'):
            href = l.xpath('./div/a/@href').extract_first()
            yield Request(href, self.parseCompany, dont_filter=True)
            # company = data.xpath('./div/p[contains(text(), "公司")]/../p[2]/a/text()').extract_first()
            # url = data.xpath('./div/p[contains(text(), "公司")]/../p[2]/a/@href').extract_first()
            # tel = data.xpath('./div/p[contains(text(), "电话")]/../p[2]/text()').extract_first()
            # address = data.xpath('./div/p[contains(text(), "地址")]/../p[2]/text()').extract_first()
        
    def parseCompany(self, response):
        item = CompanyInfoItem()
        query = response.xpath('//div[@alt="jqwlx"]/ul/li')
        company = query.xpath('./p[contains(text(), "企业")]/../p[2]/span/a/text()').extract_first()
        contact = query.xpath('./p[contains(text(), "联系")]/../p[2]/span/text()').extract_first()
        tel = query.xpath('./p[contains(text(), "电话")]/../p[2]/span/text()').extract_first()
        mobile = query.xpath('./p[contains(text(), "手机")]/../p[2]/span/text()').extract_first()
        address = query.xpath('./p[contains(text(), "企业")]/../p[2]/span/text()').extract_first()
        
        item['name'] = company
        item['contact'] = contact
        item['mobile'] = mobile
        item['tel'] = tel
        item['address'] = address
        item['url'] = response.url
        yield item

        tel2 = query.xpath('./p[contains(text(), "手机")]/../following-sibling::li[1]/p[2]/span/text()').extract_first()
        if tel2:
            item['tel'] = tel2
            yield item