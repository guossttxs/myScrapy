# -*- coding: utf-8 -*-

import pymongo
from myScrapy.items import CompanyInfoItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class MyscrapyPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    def __init__(self, mongo_uri, db_name, user_name, user_pwd):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.user_name = user_name
        self.user_pwd = user_pwd
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            db_name=crawler.settings.get('MONGODB_DBNAME'),
            user_name=crawler.settings.get('MONGODB_USER'),
            user_pwd=crawler.settings.get('MONGODB_PWD')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        self.db.authenticate(self.user_name, self.user_pwd)
    
    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        if isinstance(item, CompanyInfoItem):
            if not item.get('tel') and not item.get('mobile'):
                return item
            self.db.companys.update({'name': item.get('name')}, item, True)
        return item