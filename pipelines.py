# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import hashlib
import scrapy
import os

from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
from urllib.parse import urlparse


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instaparser

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name][item['subs_type']][item['source_name']]
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert=True)
        return item


class InstaparserImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo_url']:
            try:
                yield scrapy.Request(item['photo_url'], meta=item)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photo_url'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return str(item['subs_type']) + '/' + str(item['source_name']) + '/' + \
               str(item['user_name']) + '/' + str(item['user_name']) + '.jpg'
