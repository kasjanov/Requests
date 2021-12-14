import sys
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from shopparser import settings
from shopparser.spiders.leroymerlin import LeroymerlinSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, search=sys.argv[1])

    process.start()
