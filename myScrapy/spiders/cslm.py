from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb

'''
城市联盟
'''

class CslmSpider(Spider):
    name = 'cslmspider'

    def __init__(self, *args, **kwargs):
        super(CslmSpider, self).__init__(*args, **kwargs)
        self.domain = 'http://www.ccoo.cn/'
        self.cur_code = 0 if not rdb.get('cslm_city') else int(rdb.get('cslm_city').decode())
        self.cur_url = '' if not rdb.get('cslm_url') else rdb.get('cslm_url').decode()
        city_codes = [150,153,156,182,184,196,206,212,227,228,250,276,291,301,312,337,366,379,396,399,419,430,441,443,453,466,476,776,778,777,3251]
        if self.cur_code in city_codes:
            index = city_codes.index(self.cur_code)
            city_codes = city_codes[index:]
        self.city_codes = city_codes
        self.log('init cur_code:{} cur_url: {}'.format(self.cur_code, self.cur_url))

    def start_requests(self):
        for code in self.city_codes:
            rdb.set('cslm_city', code)
            if not self.cur_url:
                cur_url = 'http://www.ccoo.cn/yp-0-0-0-{}-1.html'.format(code)
                rdb.set('cslm_url', self.cur_url)
            else:
                cur_url = self.cur_url
                self.cur_url = ''
            self.log('访问code为{}的城市'.format(code))
            self.log('访问的URL为{}'.format(self.cur_url))
            yield Request(cur_url, self.parse, dont_filter=True)
    
    def parse(self, response):
        for r in response.xpath('//ul[@class="hy_list"]/li/div[@class="txt"]'):
            company = r.xpath('./h3/a/text()').extract_first()
            contact = r.css('p::text').re(r'联系人.*')[0]
            tel = r.css('p::text').re(r'电.?话.*')[0]
            address = r.css('p::text').re(r'地.?址.*')[0]
            
            item = CompanyInfoItem()
            tel = tel.split('：')[1].split(' ')
            for t in tel:
                if t:
                    item['name'] = company
                    item['tel'] = t
                    item['contact'] = contact
                    item['address'] = address
                    yield item
        
        next_page = ''
        for page in response.xpath('//div[@id="fenPage"]/a'):
            text = page.xpath('./text()').extract_first()
            if text == '下一页':
                next_page = page.xpath('./@href').extract_first()
        if next_page:
            url = self.domain + next_page
            rdb.set('cslm_url', url)
            yield Request(url, self.parse)
        else:
            rdb.set('cslm_url', '')



            
