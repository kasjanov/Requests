import requests
import hashlib

from lxml import html
from pprint import pprint
from pymongo import MongoClient

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}


def get_top_news_links():
    response_top = requests.get('https://news.mail.ru', headers=header)

    dom_top = html.fromstring(response_top.text)

    news_link = dom_top.xpath("//a[contains(@class, 'topnews')]/@href")
    return news_link


def get_main_news_links():
    response_main = requests.get('https://news.mail.ru', headers=header)

    dom_main = html.fromstring(response_main.text)

    news_link = dom_main.xpath("//div[@class='js-module']/ul/li[@class='list__item']//@href")
    return news_link


def parser_news_mail_ru():
    links = get_top_news_links() + get_main_news_links()

    for item in links:
        response_item = requests.get(item, headers=header)
        dom = html.fromstring(response_item.text)
        news = {}

        title = dom.xpath("//h1/text()")[0]
        source = dom.xpath("//span[@class='note']/span[@class='note__text breadcrumbs__text']/text()")[0] + \
            dom.xpath("//span[@class='note']//span[@class='link__text']/text()")[0]
        news_time = dom.xpath("//span[@class='note']/span[contains(@class,'ago')]/@datetime")[0]
        try:
            picture_url = dom.xpath("//div[@class='article-photo']//img[contains(@class,'pic')]/@src")[0]
        except IndexError:
            picture_url = ''
        text = dom.xpath("//p/text()")
        all_text = ''
        for item_text in text:
            all_text += str(item_text).replace(u'\xa0', u' ')

        news['title'] = title
        news['source'] = source
        news['news_time'] = news_time
        news['link'] = str(item)
        news['picture_url'] = picture_url
        news['text'] = all_text
        news['style'] = str(item).split('/')[3]
        news['_id'] = \
            str(hashlib.md5((news['title'] + news['link']).encode('utf-8', 'ignore')).hexdigest())

        news_list.update_one({'_id': news['_id']}, {'$set': news}, upsert=True)


client = MongoClient('127.0.0.1', 27017)
db = client['news_mail_ru']
news_list = db.news_list
parser_news_mail_ru()

for item_news in news_list.find({}):
    pprint(item_news)
