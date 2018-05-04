# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
from scrapy_zhihu.items import UserItem

class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followees_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        # url = 'https://www.zhihu.com/api/v4/members/excited-vczh/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
        # url = 'https://www.zhihu.com/api/v4/members/weirdecat?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), self.parse_user)
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
                      self.parse_followers)
        yield Request(self.followees_url.format(user=self.start_user, include=self.followees_query, offset=0, limit=20),
                      self.parse_followees)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in result.keys():
            item[field] = result.get(field)
        yield item

        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
                      self.parse_followers)
        yield Request(self.followees_url.format(user=self.start_user, include=self.followees_query, offset=0, limit=20),
                      self.parse_followees)

    def parse_followers(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') is False:
            next = results.get('paging').get('next')
            yield Request(next, self.parse_followers)

    def parse_followees(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query),
                              self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next = results.get('paging').get('next')
            yield Request(next, self.parse_followees)