# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 h-mineta <h-mineta@0nyx.net>
# This software is released under the MIT License.
#

from yatagarasu.items import MatchItem
import re
import scrapy
import mojimoji

class MatchdetailSpider(scrapy.Spider):
    name = 'matchdetail'

    allowed_domains = [
        'www.jleague.jp'
    ]
    start_urls = []

    def __init__(self, settings, *args, **kwargs):
        super(MatchSpider, self).__init__(*args, **kwargs)

        filterwarnings('ignore', category = MySQLdb.Warning)

        self.mysql_args = {
            'host'       : settings.get('MYSQL_HOST', 'localhost'),
            'port'       : settings.get('MYSQL_PORT', 3306),
            'user'       : settings.get('MYSQL_USER', 'yatagarasu'),
            'passwd'     : settings.get('MYSQL_PASSWORD', 'yatagarasupw!'),
            'db'         : settings.get('MYSQL_DATABASE', 'yatagarasu'),
            'unix_socket': settings.get('MYSQL_UNIXSOCKET', '/var/lib/mysql/mysql.sock'),
            'charset'    : 'utf8mb4'
        }

    def start_requests(self):
        connection = MySQLdb.connect(**self.mysql_args)
        connection.autocommit(False)

        if connection:
            try:
                connection.commit()
                connection.close()
            except MySQLdb.Error as ex:
                self.logger.warning(ex)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings         = crawler.settings
        )

    def parse(self, response):
        for match_selection in response.xpath('//div[@class="content"]/div[@class="main"]/section[@class="scheduleArea"]/section[@class="contentBlock"]/section[@class="matchlistWrap"]'):
            matches = match_selection.xpath('div[@class="timeStamp"]/h4/text()').re('^(\d{4})年(\d{1,2})月(\d{1,2})日')
            if matches:
                match_date = "{0:d}-{1:02d}-{2:02d}".format(int(matches[0]), int(matches[1]), int(matches[2]))

                for match_table in match_selection.xpath('table[@class="matchTable"]/tbody').xpath('tr'):
                    item = None

                    try:
                        url = match_table.xpath('td[contains(@class,"match")]/a/@href').get()
                        matches = re.match(r'^/match/([\d\w]{2,16})/(\d{4})/(\d{6})/', url)
                        if matches:
                            item = MatchItem()
                            item['url']    = matches.group(0) + 'live/'
                            item['league'] = matches.group(1)
                            item['id']     = int(matches.group(2)) * 1000000 + int(matches.group(3))
                    except Exception as ex:
                        # ID取得に失敗
                        continue

                    match_time = match_table.xpath('td[@class="stadium"]/text()').re_first(r'^(\d{2}:\d{2})')
                    if match_time:
                        item['kickoff_date']    = match_date
                        item['kickoff_time']    = match_time

                        try:
                            item['club_id_home'] = match_table.xpath('td[contains(@class,"match")]//td[@class="clubName leftside"]/a/@href').re_first(r'^/club/([^/]+)/')
                            item['club_id_away'] = match_table.xpath('td[contains(@class,"match")]//td[@class="clubName rightside"]/a/@href').re_first(r'^/club/([^/]+)/')
                        except Exception as ex:
                            # ノートが入っており、試合情報ではない場合　次trに進む
                            continue

                        item['status']          = None
                        item['club_point_home'] = None
                        item['club_point_away'] = None
                        item['stadium_name']    = mojimoji.zen_to_han(match_table.xpath('td[@class="stadium"]/a/text()').get(), kana=False)

                        try:
                            item['club_point_home'] = int(match_table.xpath('td[contains(@class,"match")]//td[@class="point leftside"]/text()').get())
                            item['club_point_away'] = int(match_table.xpath('td[contains(@class,"match")]//td[@class="point rightside"]/text()').get())
                        except Exception as ex:
                            # 試合前として扱う
                            item['club_point_home'] = None
                            item['club_point_away'] = None

                        item['status']          = match_table.xpath('td[contains(@class,"match")]//td[@class="status"]//span/@class').get()
                        yield item

                    else:
                        # 時間未定
                        continue
