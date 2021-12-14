import scrapy
import hashlib
from scrapy.http import HtmlResponse
from shopparser.items import ShopparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = []

        country_manufacture = ['Беларусь', 'Индия', 'Испания', 'Россия', 'Турция', 'Украина', 'Не+указано']
        for cm in country_manufacture:
            self.start_urls.append(f'https://leroymerlin.ru/search/?10844={cm}&q={search}')

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[contains(@aria-label,"Следующая")]//@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="product-name"]/./@href').getall()
        for link in links:
            yield response.follow(link, callback=self.shop_parse)

    def shop_parse(self, response: HtmlResponse):
        loader = ItemLoader(item=ShopparserItem(), response=response)
        loader.add_xpath('name', '//h1//text()')
        loader.add_xpath('price', '//uc-pdp-price-view//meta[@itemprop="price"]/@content')
        loader.add_xpath('currency', '//uc-pdp-price-view//meta[@itemprop="priceCurrency"]/@content')
        loader.add_xpath('unit', '//uc-pdp-price-view[@slot="primary-price"]/span[@slot="unit"]')
        loader.add_xpath('photos', '//source[@media=" only screen and (min-width: 1024px)"]/@srcset')
        loader.add_xpath('terms', "//dt/text()")
        loader.add_xpath('definitions', "//dd/text()")
        loader.add_value('link', response.url)
        loader.add_value('_id', str(hashlib.md5(str(response.url).encode('utf-8', 'ignore')).hexdigest()))
        yield loader.load_item()
