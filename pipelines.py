# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
import os

from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
from pymongo import MongoClient


class ShopparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.shopparser

    def process_price(self, price, currency, unit):
        if price:
            # c = CurrencyCodes()
            return [price, currency + '/' + unit]

    def process_item(self, item, spider):
        item['specifications'] = {item['terms'][i]: item['definitions'][i] for i in range(len(item['terms']))}
        del item['terms'], item['definitions']
        item['price'] = self.process_price(item['price'], item['currency'], item['unit'])

        del item['currency'], item['unit']
        collection = self.mongo_base[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)

        return item


class ShopparserPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return str(item['_id']) + '/' + os.path.basename(urlparse(request.url).path)
