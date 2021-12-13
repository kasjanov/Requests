import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem
from scrapy.loader import ItemLoader


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']

    def __init__(self, search, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = []
        for i in range(20):
            self.start_urls.append(
                f'https://www.labirint.ru/search/{search}/?price_min={100 * i + 1}&price_max={100 * i + 100}'
                f'&age_min=&age_max=&form-pubhouse=&lit=&stype=0&available=1&wait=1&preorder=1'
                f'&paperbooks=0&ebooks=1')
            self.start_urls.append(
                f'https://www.labirint.ru/search/{search}/?price_min={100 * i + 1}&price_max={100 * i + 100}'
                f'&age_min=&age_max=&form-pubhouse=&lit=&stype=0&available=1&wait=1&preorder=1'
                f'&paperbooks=1&ebooks=0')

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@title="Следующая"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[contains(@class,"product-title-link")]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.books_parse)

    def books_parse(self, response: HtmlResponse):
        # loader = ItemLoader(item=BookparserItem(), response=response)
        # loader.add_xpath('name', '//h1//text()')
        # loader.add_xpath('price', '//span[contains(@class,"buying-price")]//text()')
        # loader.add_xpath('author', '//a[@data-event-label="author"]/text()')
        # loader.add_xpath('editor', '//a[@data-event-label="editor"]/text()')
        # loader.add_xpath('rate', '//div[@id="rate"]/text()')
        # loader.add_xpath('annotation', '//div[@id="product-about"]/p//text()')
        # loader.add_xpath('isbn', '//div[@class="isbn"]/text()')
        # loader.add_value('link', response.url)
        # yield loader.load_item()

        name = response.xpath('//h1//text()').get()
        price = response.xpath('//span[contains(@class,"buying-price")]//text()').getall()
        link = response.url
        author = response.xpath('//a[@data-event-label="author"]/text()').get()
        editor = response.xpath('//a[@data-event-label="editor"]/text()').get()
        rate = response.xpath('//div[@id="rate"]/text()').get()
        annotation = response.xpath('//div[@id="product-about"]/p//text()').getall()
        isbn = response.xpath('//div[@class="isbn"]/text()').get()
        item = BookparserItem(name=name, price=price, link=link, author=author, isbn=isbn,
                              editor=editor, rate=rate, annotation=annotation)
        yield item
