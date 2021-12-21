# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
import os
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from scrapy.utils.python import to_bytes
import hashlib


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram_scrapy

    def write_to_db(self, item, collection_name):
        collection = self.mongo_base[collection_name]
        try:
            collection.insert_one(item)
        except Exception as e:
            print(e, item)
            pass

    def process_item(self, item, spider):
        self.write_to_db(item, spider.name)
        return item


class InstaparserImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo_url']:
            try:
                yield scrapy.Request(item['photo_url'], meta=item)
            except Exception as e:
                print(e)

    def file_path(self, request, response=None, info=None, ):
        item = request.meta
        name = item['user_name']
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()
        media_ext = os.path.splitext(url)[1]
        return f'full/{name}/%s%s.jpg' % (media_guid, media_ext)

    def item_completed(self, results, item, info):
        if results:
            item['photo_url'] = [itm[1] for itm in results if itm[0]]
        return item