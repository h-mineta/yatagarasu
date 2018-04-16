# coding: utf-8

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource,LabelSet, HoverTool
from bokeh.io import output_file, save
from bokeh.layouts import column

import MySQLdb
import pandas as pnd

def outputFigure(connection, output_dir):
    html_title = 'Yatagarasu - スコア比較'
    output_filename = __name__ + '.html'

    figure_home     = createFigureHome(connection)
    figure_away     = createFigureAway(connection)
    figure_homeaway = createFigureHomeaway(connection)

    output_file(output_dir + '/' + output_filename, html_title)
    save(column(figure_home, figure_away, figure_homeaway))

def createFigureHome(connection):
    graph_title = 'ホーム戦での得点と失点の分布(X:得点 Y:失点)'
    query_string = """
        SELECT mslt.club, ct.name, mslt.count, mslt.score, mslt.lost
        FROM (
            SELECT
            club_id_home AS club,
            'True' AS home,
            COUNT(club_point_home) AS count,
            SUM(club_point_home) AS score,
            SUM(club_point_away) AS lost
            FROM `match_tbl`
            WHERE kickoff_date BETWEEN '2018-02-22' and '2019-03-22'
            AND league IN ('j1')
            GROUP BY club_id_home
        ) AS mslt
        LEFT OUTER JOIN club_tbl AS ct ON mslt.club = ct.id
    """

    return createFigure(pnd.read_sql(query_string, connection), graph_title)

def createFigureAway(connection):
    graph_title = 'アウェー戦での得点と失点の分布(X:得点 Y:失点)'
    query_string = """
        SELECT mslt.club, ct.name, mslt.count, mslt.score, mslt.lost
        FROM (
            SELECT
             club_id_away AS club,
             COUNT(club_point_away) AS count,
             SUM(club_point_away) AS score,
             SUM(club_point_home) AS lost
            FROM `match_tbl`
            WHERE kickoff_date BETWEEN '2018-02-22' and '2019-03-22'
            AND league IN ('j1')
            GROUP BY club_id_away
        ) AS mslt
        LEFT OUTER JOIN club_tbl AS ct ON mslt.club = ct.id
    """

    return createFigure(pnd.read_sql(query_string, connection), graph_title)

def createFigureHomeaway(connection):
    graph_title = 'ホーム&アウェー戦での得点と失点の分布(X:得点 Y:失点)'
    query_string = """
        SELECT mslt.club, ct.name, SUM(mslt.count) AS count, SUM(mslt.score) AS score, SUM(mslt.lost) AS lost
        FROM (
            SELECT
             club_id_home AS club,
             'True' AS home,
             COUNT(club_point_home) AS count,
             SUM(club_point_home) AS score,
             SUM(club_point_away) AS lost
            FROM `match_tbl`
            WHERE kickoff_date BETWEEN '2018-02-22' and '2019-03-22'
            AND league IN ('j1')
            GROUP BY club_id_home
            UNION
            SELECT
             club_id_away AS club,
             'False' AS home,
             COUNT(club_point_away) AS count,
             SUM(club_point_away) AS score,
             SUM(club_point_home) AS lost
            FROM `match_tbl`
            WHERE kickoff_date BETWEEN '2018-02-22' and '2019-03-22'
            AND league IN ('j1')
            GROUP BY club_id_away
        ) AS mslt
        LEFT OUTER JOIN club_tbl AS ct ON mslt.club = ct.id
        GROUP BY mslt.club, ct.name
    """

    return createFigure(pnd.read_sql(query_string, connection), graph_title)

# 図形作成
def createFigure(df, graph_title, color=None):
    # hover tool
    hover = HoverTool(tooltips=[
        ("クラブ名", "@name"),
        ("得点", "@score"),
        ("失点", "@lost")])

    # figure作成
    plot = figure(title=graph_title,
        x_axis_label = '得点',
        y_axis_label = '失点',
        plot_width=1000,
        plot_height=600,
        tools=[hover,'pan','wheel_zoom','zoom_in','zoom_out','save','reset'],
        active_scroll='wheel_zoom')

    # ベースにデータを配置
    plot.circle(source=df,
            x='score',
            y='lost',
            size=16)

    # データに対してラベルを付ける
    labels = LabelSet(source=ColumnDataSource(df),
        x='score',
        y='lost',
        text='name',
        level='glyph',
        text_font_size="10px",
        x_offset=5,
        y_offset=5,
        render_mode='canvas')

    plot.add_layout(labels)

    return plot
