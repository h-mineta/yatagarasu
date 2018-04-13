# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class ClubItem(Item):
    id              = Field()
    name            = Field()
    url             = Field()

class MatchItem(Item):
    id              = Field()
    kickoff_date    = Field()
    kickoff_time    = Field()
    league          = Field()
    club_id_home    = Field()
    club_id_away    = Field()
    status          = Field()
    club_point_home = Field()
    club_point_away = Field()
    stadium_name    = Field()
    url             = Field()

class MatchDetailItem(Item):
    title           = Field()
