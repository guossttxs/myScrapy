from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb
import re
from myScrapy.utils.helpers import format_str

'''
中国医药网
'''

class ZgyySpider(Spider):
    name = 'zgyyspider'

    def __init__(self, *args, **kwargs):
        self.cityCode = [1114, 1117, 1111, 1129, 1138, 1122, 1125, 1120, 1139, 1134, 1132, 1131, 1116, 1124, 1137, 1115, 1112, \
            1112, 1123, 1118, 1119, 1126, 1127, 1128, 1121, 1130, 1140, 1136, 1135, 1141, 1133, 114014, 1143, 1142, 1113
        ]
        self.domain = 'http://www.pharmnet.com.cn'

    def start_requests(self):
        for code in self.cityCode:
            url = '{}/company/1/{}/1.html'.format(self.domain, code)
            yield Request(url, self.parseCompanys, dont_filter=True)

    def parseCompanys(self, response):
        for item in response.css('dd.cont'):
            contact_url = item.xpath('./ul/li[2]/a[2]/@href').extract_first()
            if contact_url:
                if contact_url.startswith(self.domain):
                    yield Request(contact_url, self.parseContact, dont_filter=True)
                else:
                    yield Request(contact_url, self.parseContact2, dont_filter=True)

        pageQuery = response.css('dd.xl span.black font')[1]
        maxPage = pageQuery.xpath('./text()').extract_first()
        maxPage = 1 if not maxPage else int(maxPage)

        urls = response.url.split('/')
        html_name = urls[-1]
        cur_page = html_name.split('.')[0]
        cur_page = 1 if not cur_page else int(cur_page)

        if cur_page < maxPage:
            urls[-1] = '{}.html'.format(cur_page+1)
            url = '/'.join(urls)
            #yield Request(url, self.parseCompanys, dont_filter=True)
        
    def format_query(self, query):
        query = query.split('：')
        if len(query) > 1:
            query[0] = "".join(query[0].split())
            return query
        else:
            return ''

    def parseContact(self, response):
        content = response.css('div.jb ul')
        name = content.xpath('./li[2]/h2/text()').extract_first()
        contact = ''
        tel = ''
        mobile = ''
        address = ''
        url = response.url
        if name:
            for lq in content.xpath('./li/text()').extract():
                lq = self.format_query(lq)
                if lq:
                    if lq[0].find('联系人') >= 0:
                        contact = lq[1]
                    elif lq[0].find('联系电话') >= 0:
                        tel = lq[1]
                    elif lq[0].find('手机') >= 0:
                        mobile = lq[1]
                    elif lq[0].find('单位地址') >= 0:
                        address = lq[1]
            item = CompanyInfoItem()
            item['name'] = name
            item['contact'] = contact
            item['tel'] = tel
            item['mobile'] = mobile
            item['address'] = address
            item['url'] = url
            item['meta'] = 'zgyy'
            yield item

    def parseContact2(self, response):
        query = response.css('div.lxfs dl dd ul')
        item = CompanyInfoItem()
        for q in query.xpath('./li/text()').extract():
            q = self.format_query(q)
            if len(q) > 1:
                if q[0].find('公司名称') >= 0:
                    item['name'] = q[1]
                elif q[0].find('联系人') >= 0:
                    item['contact'] = q[1]
                elif q[0].find('联系电话') >= 0:
                    item['mobile'] = q[1]
                elif q[0].find('联系地址') >= 0:
                    item['address'] = q[1]
                elif q[0].find('手机') >= 0:
                    item['tel'] = q[1]
        item['url'] = response.url
        item['meta'] = 'zgyy'
        yield item