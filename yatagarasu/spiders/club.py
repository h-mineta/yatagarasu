# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 h-mineta <h-mineta@0nyx.net>
# This software is released under the MIT License.
#

from yatagarasu.items import ClubItem
import re
import scrapy
import mojimoji

class ClubSpider(scrapy.Spider):
    name = 'club'

    allowed_domains = [
        'www.jleague.jp'
    ]
    start_urls = [
        'https://www.jleague.jp/club/'
    ]

    def parse(self, response):
        for club in response.xpath('//div[@class="content"]/div[@class="main"]/section[@class="clubArea"]/section[contains(@class,"clubTeamArea")]/ul/li/a'):
            item = ClubItem()
            item['id'] = club.xpath('@href').re_first(r'^/club/([^/]+)/')
            item['name'] = mojimoji.zen_to_han(club.xpath('text()').get(), kana=False)
            item['url'] = club.xpath('@href').get()
            yield item
