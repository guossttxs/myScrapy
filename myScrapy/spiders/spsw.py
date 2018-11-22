from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb
import re
from myScrapy.utils.helpers import format_str

'''
食品商务网
'''

class SpswSpider(Spider):
    name = 'spswspider'
    
    def __init__(self, *args, **kwargs):
        self.domain = 'http://www.21food.cn'

    def start_requests(self):
        srcurl = 'http://www.21food.cn/company/'
        # yield Request(url, self.parse)
        citys = ['search_province-%C1%C9%C4%FE.html', 'search_province-%BC%AA%C1%D6.html', 'search_province-%BA%DA%C1%FA%BD%AD.html']
        for i in citys:
            url = srcurl + i
            yield Request(url, self.parseCityList, dont_filter=True)

    def parse(self, response):
        for li in response.css('div.ind_k_top_r div.ind_k_r_mpcc ul li'):
            for href in li.xpath('./span/a/@href').extract():
                url = self.domain + href
                yield Request(url, self.parseCityList, dont_filter=True)

    def parseCityList(self, response):
        for dd in response.css('div.qy_list_main.auto div dl dd'):
            imgTitle = dd.css('div.qy_ls_lf div.qy_ls_rzlx img.bn_ls1::attr(title)').extract_first()
            if not imgTitle:
                url = dd.css('div.qy_ls_lf div.qy_ls_l_tit span.qylis_tt a::attr(href)').extract_first()
                yield Request(url, self.parseCompany, dont_filter=True)
            elif imgTitle == '实名备案':
                url = dd.css('div.qy_ls_lf div.qy_ls_l_tit em a::attr(href)').extract_first()
                url = self.domain + url
                yield Request(url, self.parseCompanyYWeb, dont_filter=True)
        
        page = response.css('div.content.content_prod div.product_top_t div.qy_list_main.auto div.page')
        next_page = page.xpath('./a[contains(text(), "下一页")]/@href').extract_first()
        if next_page:
            url = self.domain + next_page
            yield Request(url, self.parseCityList, dont_filter=True)

    def parseCompany(self, response):
        '''
        企业未实名认证 网页解析
        '''
        tables = response.css('table.menu_bg tr')
        if not tables:
            tables = response.css('table.menu_bg tbody tr')
        if tables:
            contact_url = tables.xpath('./td/a[contains(text(), "联系方式")]/@href').extract_first()
            if contact_url:
                yield Request(contact_url, self.parseCompanyInfo, dont_filter=True)

    def parseCompanyInfo(self, response):
        '''
        企业联系方式网页获取
        '''
        name = response.css('table.banner tr td.f26_black span').xpath('./text()').extract_first()
        name = format_str(name) if name else ''
        
        contact = ''
        address = ''
        tel = ''
        mobile = ''

        for q in response.css('div.contact div.contact-info div'):
            label = q.xpath('./label/text()').extract_first()
            text = "".join(q.xpath('./text()').extract())
            text = format_str(text)
            if label.find('联系人') == 0:
                contact = text
            elif label.find('地址') == 0:
                address = text
            elif label.find('电话') == 0:
                tel = text
            elif label.find('手机') == 0:
                mobile = text
        if name:
            item = CompanyInfoItem()
            item['name'] = name
            item['contact'] = contact
            item['address'] = address
            item['tel'] = tel
            item['mobile'] = mobile
            item['url'] = response.url
            item['meta'] = 'spsw'
            yield item

    def parseCompanyYWeb(self, response):
        '''
        企业实名认证 黄页解析
        '''
        name = ''
        tel = ''
        mobile = ''
        address = ''
        contact = ''
        query = response.css('div.y_main_lf')
        content = query.xpath('./div[@class="y_lfdet_tit"]/span[contains(text(), "联系方式")]/..').xpath('following-sibling::div[@class="y_l_cont clearfix"]')[0]
        if content:
            for ll in content.css('div.y_l_cont_ll ul li'):
                emt = ll.xpath('./em/text()').extract_first()
                spant = ll.xpath('./span/text()').extract_first()
                if emt:
                    if emt.find('名称') == 0:
                        name = spant
                    elif emt.find('电话') == 0:
                        tel = spant
                    elif emt.find('手机') == 0:
                        mobile = spant
            for rr in content.css('div.y_r_cont_rr ul li'):
                emt = rr.xpath('./em/text()').extract_first()
                spant = rr.xpath('./span/text()').extract_first()
                if emt:
                    if emt.find('业务主管') == 0:
                        contact = spant
                    elif emt.find('地址') == 0:
                        address = spant
        item = CompanyInfoItem()
        item['name'] = name
        item['tel'] = tel
        item['mobile'] = mobile
        item['address'] = address
        item['contact'] = contact
        item['url'] = response.url
        item['meta'] = 'spsw'
        yield item
        
        
            