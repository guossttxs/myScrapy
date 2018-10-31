from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb
import re
from myScrapy.utils.helpers import format_str

'''
八方资源
'''

class BfzySpider(Spider):
    name = 'bazyspider'

    def __init__(self, *args, **kwargs):
        self.citys = ['beijing', 'tianjin', 'shanghai', 'chongqing', 'xianggang', 'aomen', 'taiwan', 'hainan', 'jiangsu', 'hebei', 'shanxi', \
            'neimeng', 'liaoning', 'jilin', 'heilongjiang', 'zhejiang', 'anhui', 'fujian', 'jiangxi', 'shandong', 'henan', 'hubei', 'hunan', \
            'guangdong', 'guangxi', 'sichuan', 'guizhou', 'yunnan', 'xizang', 'shanxisheng', 'gansu', 'qinghai', 'ningxia', 'xinjiang'
        ]
        self.domain = 'https://www.b2b168.com'
        super(BfzySpider, self).__init__(*args, **kwargs)
 
    def start_requests(self):
        for city in self.citys:
            url = '{}/{}qiye/'.format(self.domain, city)
            yield Request(url, self.parseCity, dont_filter=True)

    def parseCity(self, response):
        for dd in response.css('div.mach_list dl dd'):
            if dd:
                for href in dd.xpath('./a'):
                    url = href.xpath('./@href').extract_first()
                    url = self.domain + url
                    yield Request(url, self.parseCompanys, dont_filter=True)
    
    def parseCompanys(self, response):
        for company in response.css('ul.list li div.biaoti a'):
            href = company.xpath('./@href').extract_first()
            if href.startswith('//'):
                href = 'https:' + href
            elif not href.startswith('http'):
                href = 'https://' + href

            if href.startswith(self.domain):
                yield Request(href, self.parseNormalCompany, dont_filter=True)
            else:
                href = href + 'contact.aspx'
                yield Request(href, self.parseCompany, dont_filter=True)


        pages_query = response.css('div.pages')
        pages = response.css('div.pages::text').extract_first()
        maxCount = re.findall('\d+', pages)[0]
        maxCount = 1 if not maxCount else int(maxCount)
        curPage = pages_query.css('a.one::text').extract_first()
        curPage = 1 if not curPage else int(curPage)
        
        if curPage < maxCount:
            if pages_query.xpath('./a[1]/text()').extract_first() != '首页':
                next_page = pages_query.xpath('./a[{}]/@href'.format(curPage+1)).extract_first()
            else:
                next_page = pages_query.xpath('./a[{}]/@href'.format(curPage+2)).extract_first()
                if pages_query.xpath('./a[2]/text()').extract_first() == '上页':
                    next_page = pages_query.xpath('./a[{}]/@href'.format(curPage+3)).extract_first()
            url = self.domain + next_page
            yield Request(url, self.parseCompanys, dont_filter=True)

    def parseCompany(self, response):
        item = CompanyInfoItem()
        
        query = response.css('li.Contact')
        name = query.xpath('./a[1]/text()').extract_first()

        contact = query.xpath('./a[2]/text()').extract_first()
        contact = contact if contact else ''
        contact = format_str(contact)

        text_query = query.xpath('./text()').extract()
        
        tel = ""
        mobile = ""
        address = ""

        for q in text_query:
            q = "".join(q.split())
            q = q.split('：')
            if len(q) == 2:
                if q[0].startswith('电话'):
                    tel = q[1]
                elif q[0].startswith('移动电话'):
                    mobile = q[1]
                elif q[0].startswith('地址'):
                    address = q[1]
        
        item['name'] = name
        item['address'] = address
        item['tel'] = tel
        item['mobile'] = mobile
        item['url'] = response.url
        item['contact'] = contact
        item['meta'] = 'bfzy'

        yield item


    def parseNormalCompany(self, response):
        item = CompanyInfoItem()
        name = response.css('ul#lxfs::text').extract_first()
        name = name.replace('的联系方式', '')
        name = name.replace('联系方式', '')

        query = response.css('dl.codl')
        address =  query.xpath('./dd[1]/text()').extract()
        address = format_str(''.join(address))

        tel = query.xpath('./dd[2]/text()').extract_first()
        tel = tel if tel else ''
        tel = format_str(tel)

        contact = query.xpath('./dd[3]/text()').extract_first()
        contact = contact if contact else ''
        contact = format_str(contact)

        mobile = query.xpath('./dd[4]/text()').extract_first()
        mobile = mobile if mobile else ''
        mobile = format_str(mobile)

        item['name'] = name
        item['address'] = address
        item['tel'] = tel
        item['mobile'] = mobile
        item['url'] = response.url
        item['contact'] = contact
        item['meta'] = 'bfzy'
        yield item
