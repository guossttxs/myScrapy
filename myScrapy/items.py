# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CompanyInfoItem(scrapy.Item):
    #企业信息item
    name = scrapy.Field()
    mobile = scrapy.Field()
    tel = scrapy.Field()
    address = scrapy.Field()
    contact = scrapy.Field()
    url = scrapy.Field()

