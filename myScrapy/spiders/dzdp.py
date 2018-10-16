from scrapy import Spider, Request
from myScrapy.items import CompanyInfoItem
from myScrapy.redis import rdb
import pickle

'''
大众点评
'''

class DzdpSpider(Spider):
    name = 'dzdp'

    def __init__(self):
        self.classify = [33958, 33762, 195, 2928, 836, 33971, 34003, 33986, 3066, 33976, 197, 3064, 34031, 33965, 979, 26491]

    def start_requests(self):
        citys = rdb.lrange('dzdp_citys', 0, -1)
        if citys:
            self.getCityChannel(citys)
        else:
            url = 'http://www.dianping.com/citylist'
            yield Request(url, callback=self.parseCitys, dont_filter=True)
    
    def parseCitys(self, response):
        '''
        获取城市列表的URL，并存到redis
        '''
        for city in response.xpath('//div[@class="main-citylist"]/ul/li/div[@class="terms"]/div[@class="findHeight"]/a'):
            cn_name = city.xpath('./text()').extract_first()
            src_href = city.xpath('./@href').extract_first()
            href = 'http:{}/ch80'.format(src_href)
            en_name = src_href.split('/')[-1]
            data = pickle.dumps({'cn_name': cn_name, 'href': href, 'en_name': en_name})
            rdb.rpush('dzdp_citys', data)

        self.getCityChannel()

    def getCityChannel(self, citys=None):
        if not citys:
            citys = rdb.lrange('dzdp_citys', 0, -1)
        for data in citys:
            self.log('请求获取城市频道: {}'.format(data))
            data = pickle.loads(data)
            rdb.set('dzdp_cur_city', data.get('en_name'))
            href = data.get('href')
            for i in self.classify[:1]:
                href = '{}/g{}'.format(href, i)
                yield Request(href, callback=self.parseItems, dont_filter=True)
    
    def parseCityChannel(self, response):
        '''
        获取城市的频道（美食，电影，休闲等）
        '''
        city = rdb.get('dzdp_cur_city')
        if isinstance(city, bytes):
            city = city.decode()
        channels = response.css('div.J_filter_channel div.nc-contain div div a')
        for channel in channels:
            name = channel.xpath('./text()').extract_first()
            href = channel.xpath('./@href').extract_first()
            data = pickle.dumps({'name': name, 'href': href})
            key = 'dzdp_{}_channels'.format(city)
            rdb.rpush(key, data)
            hkey = '{}_hash'.format(key)
            rdb.hset(hkey, name, href)
        
        self.getChannelClassify(city, None, '生活服务')
    
    def getChannelClassify(self, city, channels=None, specialName=''):
        if not specialName:
            if not channels:
                key = 'dzdp_{}_channels'.format(city)
                channels = rdb.lrange(key, 0, -1)
            for channel in channels:
                key = 'dzdp_{}_cur_channel'.format(city)
                self.log('获取频道的分类信息:{}'.format(channel))
                channel = pickle.loads(channel)
                rdb.rset(key, channel.get('name'))
                yield Request(channel.get('href'), self.parseClassify, dont_filter=True)
        else:
            key = 'dzdp_{}_channels_hash'.format(city)
            channel_href = rdb.hget(key, specialName)
            self.log('获取{}频道分类信息:{}'.format(specialName, channel_href))
            yield Request(channel_href, self.parseClassify, dont_filter=True)
    
    def parseClassify(self, response):
        pass

    def parseItems(self, response):
        pass





