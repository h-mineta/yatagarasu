# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 h-mineta <h-mineta@0nyx.net>
# This software is released under the MIT License.
#

import re
import scrapy
import mojimoji
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class MatchDetailSpider(CrawlSpider):
    name = 'match_detail'

    allowed_domains = [
        'www.jleague.jp'
    ]
    start_urls = [
        'https://www.jleague.jp/match/search/j1/all/'
    ]

    #この条件に合うリンクは巡回
    list_allow = [
        r'/match/search/j[12](.+?)/all/',
    ]
    list_deny  = [
        r'/match/search/(.+?)/all/.+'
    ]

    list_allow_parse = [r'/match/j[12].+/(\d{4})/(\d{6})/live/']  #データ抽出するリンク指定
    list_deny_parse  = []

    rules = (
        # 巡回ルール。
        Rule(LinkExtractor(
            allow    = list_allow,
            deny     = list_deny,
            ),
            follow   = True # そのリンクへ入っていく
        ),
        # データ抽出ルール
        Rule(LinkExtractor(
            allow    = list_allow_parse,
            deny     = list_deny_parse,
            unique   = True # おなじリンク先ではデータ抽出しない
            ),
            callback ='parse_items' # 条件に合えば、ここで指定したデータ抽出実行関数を実行する。
        ),
    )

    def parse_items(self, response):
        # yield {
        #     'title':response.xpath('//title/text()').get()
        # }
        print(response.url)
        pass
