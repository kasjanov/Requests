# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
# from itemloaders.processors import MapCompose, TakeFirst


class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    author = scrapy.Field()
    editor = scrapy.Field()
    rate = scrapy.Field()
    annotation = scrapy.Field()
    price_all = scrapy.Field()
    price_you = scrapy.Field()
    currency = scrapy.Field()
    isbn = scrapy.Field()
    _id = scrapy.Field()
