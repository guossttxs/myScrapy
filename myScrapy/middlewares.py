# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import random
import requests
from myScrapy.redis import rdb

class MyscrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyscrapyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class HttpUserAgentMiddleware(object):
    '''
    设置user-agent属性
    '''
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        agents = crawler.settings.getlist('USER_AGENTS')
        return cls(agents)

    def process_request(self, request, spider):
        agent = random.choice(self.agents)
        print('get user-agent:', agent)
        request.headers.setdefault('User-Agent', agent)
        # request.headers.setdefault('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
        # request.headers.setdefault('Accept-Language', 'zh-CN,zh;q=0.9,en;q=0.8')
        # request.headers.setdefault('Cookie', 's_ViewType=10; _lxsdk_cuid=1667b9ce888c8-04920f983b4ff6-346a7809-fa000-1667b9ce88ac8; _lxsdk=1667b9ce888c8-04920f983b4ff6-346a7809-fa000-1667b9ce88ac8; _hc.v=6b7c6d04-6b14-cfea-8781-abb863759d1d.1539672173; _lxsdk_s=1667b9ce88c-73a-c16-ed%7C%7C22')


class HttpProxyRequestMiddleware(object):
    '''
    设置访问代理
    '''
    def process_request(self, request, spider):
        proxy_addr = self.get_new_proxy()
        print('get proxy addr:', proxy_addr)
        if proxy_addr:
            request.meta['proxy'] = proxy_addr

    def get_new_proxy(self):
        proxy = rdb.get('proxy')
        if not proxy:
            proxy = requests.get("http://182.92.190.100:5010/get/").content
            if proxy:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode()
                return 'http://' + proxy
        return proxy.decode()


class HttpRetryMiddleware(RetryMiddleware):
    '''
    错误处理，重试设置
    '''
    def del_new_proxy(self, proxy):
        if proxy:
            if proxy.startswith('http://'):
                proxy = proxy.split('//')[1]
            requests.get("http://182.92.190.100:5010/delete/?proxy={}".format(proxy))

    def process_response(self, request,  response, spider):
        #对返回结果进行判断 异常时删除代理
        if request.meta.get('dont_retry', False):
            return response
        proxy = request.meta.get('proxy', False)
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            spider.logger.warning(reason)
            self.del_new_proxy(proxy)
            return self._retry(request, reason, spider) or response
        if proxy:
            rdb.set('proxy', proxy)
            rdb.expire('proxy', 3000)
        return response

    def process_exception(self, request, exception, spider):
        #连接异常时处理
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
            and not request.meta.get('dont_retry', False):
            spider.logger.warning('连接异常，正在重试')
            self.del_new_proxy(request.meta.get('proxy', False))
            return self._retry(request, exception, spider)
