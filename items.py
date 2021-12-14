# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy
import re
from scrapy.loader.processors import TakeFirst, MapCompose


def edit_definitions(values):
    pattern = re.compile('\\n +')
    values = re.sub(pattern, '', values)
    try:
        return float(values)
    except ValueError:
        return values


def edit_unit(values):
    try:
        return values.split('>')[1].split('<')[0]
    except ValueError:
        return values


class ShopparserItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose())
    terms = scrapy.Field(input_processor=MapCompose())
    definitions = scrapy.Field(input_processor=MapCompose(edit_definitions))
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose())
    currency = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose())
    unit = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(edit_unit))
    specifications = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())

