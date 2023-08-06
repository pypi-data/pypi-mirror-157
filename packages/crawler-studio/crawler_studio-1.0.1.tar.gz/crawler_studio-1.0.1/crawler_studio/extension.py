"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/6/12 下午10:24
"""
from scrapy import signals
import logging
from .stats import SpiderStats

logger = logging.getLogger(__name__)


class ScrapyMonitor(object):

    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler)

        # connect the oension object to signals
        crawler.signals.connect(o.spider_opened,
                                signal=signals.spider_opened)

        crawler.signals.connect(o.spider_closed,
                                signal=signals.spider_closed)

        crawler.signals.connect(o.log_request,
                                signal=signals.request_reached_downloader)

        crawler.signals.connect(o.log_response,
                                signal=signals.response_downloaded)

        crawler.signals.connect(o.item_scraped,
                                signal=signals.item_scraped)

        crawler.signals.connect(o.item_dropped,
                                signal=signals.item_dropped)

        crawler.signals.connect(o.item_error,
                                signal=signals.item_error)

        return o

    def spider_opened(self, spider):
        self.stats_sender = SpiderStats(self.crawler, spider)
        self.stats_sender.spider_open(spider)

    def spider_closed(self, spider, reason):
        self.stats_sender.spider_close(spider, reason)

    def log_request(self, request, spider):
        pass

    def log_response(self, response, request, spider):
        pass

    def item_scraped(self, item, response, spider):
        pass

    def item_dropped(self, item, response, spider):
        pass

    def item_error(self, item, response, spider):
        pass
