# -*- coding: utf-8 -*-

#
# Copyright (c) 2018 h-mineta <h-mineta@0nyx.net>
# This software is released under the MIT License.
#
import MySQLdb
from warnings import filterwarnings

class MysqlPipeline(object):
    def __init__(self, settings, *args, **kwargs):
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

        self.initialize()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings         = crawler.settings,
        )

    def initialize(self):
        self.connection = MySQLdb.connect(**self.mysql_args)
        self.connection.autocommit(False)

        with self.connection.cursor() as cursor:

            sql_create_tbl = '''
                CREATE TABLE IF NOT EXISTS `club_tbl` (
                `id` varchar(64) NOT NULL,
                `name` varchar(255) NOT NULL,
                `url` text NULL,
                `update_time` timestamp NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`id`),
                KEY (`name`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='クラブ情報テーブル' ROW_FORMAT=DYNAMIC;
            '''
            cursor.execute(sql_create_tbl)

            sql_create_tbl = '''
                CREATE TABLE IF NOT EXISTS `match_tbl` (
                `id` bigint(1) UNSIGNED NOT NULL,
                `kickoff_date` date NOT NULL,
                `kickoff_time` time NULL,
                `league` varchar(16) NOT NULL,
                `club_id_home` varchar(64) NOT NULL,
                `club_id_away` varchar(64) NOT NULL,
                `status` varchar(16) NOT NULL,
                `club_point_home` int(1) UNSIGNED NULL,
                `club_point_away` int(1) UNSIGNED NULL,
                `stadium_name`varchar(128) NULL,
                `url` text NULL,
                `update_time` timestamp NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`id`),
                UNIQUE KEY `unique_match` (`kickoff_date`, `club_id_home`, `club_id_away`),
                FOREIGN KEY `club_id_home` (`club_id_home`) REFERENCES club_tbl (`id`),
                FOREIGN KEY `club_id_away` (`club_id_away`) REFERENCES club_tbl (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='試合テーブル' ROW_FORMAT=DYNAMIC;
            '''
            cursor.execute(sql_create_tbl)

            sql_create_tbl = '''
                CREATE TABLE IF NOT EXISTS `match_detail_tbl` (
                `match_id` bigint(1) UNSIGNED NOT NULL,
                `stadium_name`varchar(255) NULL,
                `stadium_wether`varchar(255) NULL,
                `url` text NULL,
                `update_time` timestamp NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`match_id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='試合詳細テーブル' ROW_FORMAT=DYNAMIC;
            '''
            #cursor.execute(sql_create_tbl)

            sql_create_tbl = '''
                CREATE TABLE IF NOT EXISTS `toto_tbl` (
                `id` int(1) UNSIGNED NOT NULL AUTO_INCREMENT,
                `held_name` varchar(255) NOT NULL,
                `held_count` int(1) UNSIGNED NOT NULL,
                `sales_start_datetime` datetime NOT NULL,
                `update_time` timestamp NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`id`),
                UNIQUE KEY (`held_name`),
                KEY (`held_count`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='totoくじプテーブル' ROW_FORMAT=DYNAMIC;
            '''
            # 20180325 inactive
            #cursor.execute(sql_create_tbl)

            sql_create_tbl = '''
                CREATE TABLE IF NOT EXISTS `toto_match_tbl` (
                `id` int(1) UNSIGNED NOT NULL AUTO_INCREMENT,
                `toto_id` int(1) UNSIGNED NOT NULL,
                `toto_match_number` int(1) UNSIGNED NOT NULL,
                `match_id` bigint(1) UNSIGNED NOT NULL,
                `update_time` timestamp NOT NULL DEFAULT current_timestamp(),
                PRIMARY KEY (`id`),
                UNIQUE KEY `unique_toto_match` (`toto_id`, `toto_match_number`),
                FOREIGN KEY `toto_id` (`toto_id`) REFERENCES toto_tbl (`id`),
                FOREIGN KEY `match_id` (`match_id`) REFERENCES match_tbl (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='totoくじ詳細プテーブル' ROW_FORMAT=DYNAMIC;
            '''
            # 20180325 inactive
            #cursor.execute(sql_create_tbl)

            self.connection.commit()

        self.connection.close()
        self.connection = None

    def open_spider(self, spider):
        self.connection = MySQLdb.connect(**self.mysql_args)
        self.connection.autocommit(False)

    def close_spider(self, spider):
        if self.connection:
            try:
                self.connection.commit()
                self.connection.close()
            except MySQLdb.Error as ex:
                self.logger.warning(ex)

    def process_item(self, item, spider):
        if spider.name in ['club']:
            self.process_item_club(item, spider)
        elif spider.name in ['match']:
            self.process_item_match(item, spider)
        elif spider.name in ['match_detail']:
            self.process_item_match_detail(item, spider)

        return item

    def process_item_club(self, item, spider):
        sql_insert = '''
            INSERT INTO club_tbl(
                id,
                name,
                url
            )
            VALUES(
                %s,
                %s,
                %s
            )
            ON DUPLICATE KEY UPDATE
                name = VALUES(name)
            ;
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql_insert,(
                    item['id'],
                    item['name'],
                    item['url']
                    ))

        except MySQLdb.Error as ex:
            self.connection.rollback()
            self.logger.error(ex)

    def process_item_match(self, item, spider):
        sql_insert = '''
            INSERT IGNORE INTO match_tbl(
                id,
                kickoff_date,
                kickoff_time,
                league,
                club_id_home,
                club_id_away,
                status,
                club_point_home,
                club_point_away,
                stadium_name,
                url
            )
            VALUES(
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            ON DUPLICATE KEY UPDATE
                kickoff_time    = VALUES(kickoff_time),
                status          = VALUES(status),
                club_point_home = VALUES(club_point_home),
                club_point_away = VALUES(club_point_away)
            ;
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql_insert,(
                    item['id'],
                    item['kickoff_date'],
                    item['kickoff_time'],
                    item['league'],
                    item['club_id_home'],
                    item['club_id_away'],
                    item['status'],
                    item['club_point_home'],
                    item['club_point_away'],
                    item['stadium_name'],
                    item['url']
                    ))

        except MySQLdb.Error as ex:
            self.connection.rollback()
            self.logger.error(ex)

    def process_item_match_detail(self, item, spider):
        pass
