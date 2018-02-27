#!/usr/bin/env python3
# -*- coding:UTF-8 -*-

# 官方
import json

# tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from config import DEFAULT_SELECT_LIMIT, API_PORT
from db.SqlHelper import SqlHelper as SqlHelper
from api.tornadoLog import logger, init_log

sqlhelper = SqlHelper()


class GetProxy(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        count = self.get_argument('count', DEFAULT_SELECT_LIMIT)
        use_flag = self.get_argument('use_flag', 'default')

        self.write(json.dumps(
            sqlhelper.select(count=int(count), use_flag=use_flag))
        )


class Used(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        proxy_id = self.get_argument('proxy_id', None)
        is_succ = self.get_argument('is_succ', None)
        speed = self.get_argument('speed', None)
        use_flag = self.get_argument('use_flag', 'default')

        if proxy_id and is_succ and speed:
            sqlhelper.update(int(proxy_id),
                             True if is_succ.lower().find('f') == -1 else False,
                             int(speed),
                             use_flag)
            self.write('submit')
        else:
            self.write('error')


def start_api_server():
    """
    状态web
    :return:
    """

    init_log()

    # 默认配置
    define("port", default=API_PORT, help="run on the given port", type=int)

    tornado.options.parse_command_line()

    # 路由
    app = tornado.web.Application(handlers=[
        (r"/", GetProxy),
        (r"/get", GetProxy),
        (r"/used", Used)
    ])
    http_server = tornado.httpserver.HTTPServer(app)

    # 监听端口
    http_server.listen(options.port)

    logger.info("status web run with :%d" % options.port)

    # 开始
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    start_api_server()
