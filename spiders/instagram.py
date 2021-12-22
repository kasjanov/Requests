import json
import hashlib
import re
import scrapy

from copy import deepcopy
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from scrapy.utils.python import to_bytes
from scrapy.http import HtmlResponse


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']

    insta_login = 'zakaz_tortiki_msk'
    insta_pwd = '#PWD_INSTAGRAM_BROWSER:10:1640082537:AfVQABa32pM6quqROviuSoX0xtgvY0D/zlEWLt9hbnV1ASojeJUjr6EdBn9' \
                'lzsXAejkCcHXenZ5rzROtayzNkE0hE5Uqnx7sFqT8cpVBm5JZXGlf7DFYdLBU/p2O11woMIwmnLJ8CqVF3h5+GKc='
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_link = 'https://www.instagram.com/graphql/query/?'
    followers_link = 'https://i.instagram.com/api/v1/friendships/'

    subscribers_hash = 'c76146de99bb02f6415203be841dd25a'
    subscriptions_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    def __init__(self, users_list):
        self.users_list = users_list

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.insta_login,
                      'enc_password': self.insta_pwd},
            headers={'x-csrftoken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users_list:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'username': username,
                     'count': 12,
                     'next_max_id': ''
                     }

        url_followers = f'{self.followers_link}{user_id}/followers/?count=12&search_surface=follow_list_page'

        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(variables)
                       },
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}
        )

        url_following = f'{self.followers_link}{user_id}/following/?count=12'
        yield response.follow(
            url_following,
            callback=self.following_parse,
            cb_kwargs={'user_id': user_id,
                       'username': username,
                       'variables': deepcopy(variables)
                       },
            headers={'User-Agent': 'Instagram 155.0.0.37.107'}

        )

    def followers_parse(self, response: HtmlResponse, user_id, username, variables):
        j_body = json.loads(response.text)
        variables['next_max_id'] = j_body.get('next_max_id')

        if variables['next_max_id']:

            url_followers = f'{self.followers_link}{user_id}/followers/?count=12&' \
                            f'max_id={variables["next_max_id"]}&search_surface=follow_list_page'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)
                           },
                headers={'User-Agent': 'Instagram 155.0.0.37.107'}
            )

        followers = j_body.get('users')
        for follower in followers:
            item = InstaparserItem(
                _id=str(hashlib.sha1(to_bytes(str(follower['pk']))).hexdigest()),
                source_id=user_id,
                source_name=username,
                user_id=follower['pk'],
                user_name=follower['username'],
                user_fullname=follower['full_name'],
                photo_url=follower['profile_pic_url'],
                subs_type='follower'
            )

            yield item

    def following_parse(self, response, user_id, username, variables):
        j_body = json.loads(response.text)
        variables['next_max_id'] = j_body.get('next_max_id')

        if variables['next_max_id']:
            url_following = f'{self.followers_link}{user_id}/following/?count=12&' \
                            f'max_id={variables["next_max_id"]}&search_surface=follow_list_page'

            yield response.follow(
                url_following,
                callback=self.following_parse,
                cb_kwargs={'user_id': user_id,
                           'username': username,
                           'variables': deepcopy(variables)
                           },
                headers={'User-Agent': 'Instagram 155.0.0.37.107'}
            )

        followings = j_body.get('users')
        for following in followings:
            item = InstaparserItem(
                _id=str(hashlib.sha1(to_bytes(str(following['pk']))).hexdigest()),
                source_id=user_id,
                source_name=username,
                user_id=following['pk'],
                user_name=following['username'],
                user_fullname=following['full_name'],
                photo_url=following['profile_pic_url'],
                subs_type='following'
            )

            yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
