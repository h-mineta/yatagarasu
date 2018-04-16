#!/usr/bin/python3
# coding: utf-8

import os
import importlib

import MySQLdb

args = {
    'plugins_dir':'exporter_plugins',
    'outputs_dir':'exporter_outputs'
}

args['mysql_args'] = {
    'host'       : 'eins.0nyx.net',
    'user'       : 'yatagarasu',
    'passwd'     : 'yatagarasupw!',
    'db'         : 'yatagarasu',
    'charset'    : 'utf8mb4'
}

def main(args):
    plugins = os.listdir(args['plugins_dir'])

    connection = MySQLdb.connect(**args['mysql_args'])
    for plugin in plugins:
        if plugin.endswith('.py') == False:
            continue
        path = os.path.splitext(args['plugins_dir'] + '/' + plugin)[0].replace(os.path.sep, '.')

        print(path)
        module = importlib.import_module(path)
        module.outputFigure(connection, args['outputs_dir'])

    if connection:
        try:
            connection.close()
        except MySQLdb.Error as ex:
            print("Connection close failed")

if __name__ == '__main__':
    main(args)
