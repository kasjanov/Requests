# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import hashlib
from pymongo import MongoClient


class BookparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):
        item['price_all'], item['price_you'], item['currency'] = self.process_price(item['price'])
        del item['price']
        item['annotation'] = self.process_annotation(item['annotation'])
        item['rate'] = float(item['rate'])
        item['_id'] = str(hashlib.md5((item['name'] + item['link']).encode('utf-8', 'ignore')).hexdigest())
        collection = self.mongobase[spider.name]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item

    def process_price(self, price):
        if price:
            if price[0] == 'Цена':
                return int(price[1]), int(price[1]), price[3]
            else:
                return int(price[0]), int(price[1]), price[2]
        else:
            return None, None, None

    def process_annotation(self, annotation):
        full_annotation = ''
        for an in annotation:
            full_annotation += an
        return full_annotation
