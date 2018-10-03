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
from api.tornadoLog import logger, init_tornado_log

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

    def post(self):
        data = json.loads(self.request.body.decode())

        proxy_id = data.get('id', None)
        is_succ = data.get('is_succ', None)
        speed = data.get('speed', None)
        use_flag = data.get('use_flag', 'default')

        if proxy_id and is_succ and speed is not None:
            sqlhelper.update(int(proxy_id),
                             True if is_succ.lower().find('f') == -1 else False,
                             float(speed),
                             use_flag)
            self.write('submit')
        else:
            logger.error('used post error -- %s' % self.request.body)
            self.write('error')


class StatusWeb(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        res = """<html><head><meta charset="UTF-8"><title>IPProxy Used Status</title>
        <!--meta http-equiv="refresh" content="60"-->
        <style>
        /* Border styles */
        #table-1 thead, #table-1 tr {
            border-top-width: 1px;
            border-top-style: solid;
            border-top-color: rgb(230, 189, 189);
        }
        #table-1 {
            border-bottom-width: 1px;
            border-bottom-style: solid;
            border-bottom-color: rgb(230, 189, 189);
        }
        /* Padding and font style */
        #table-1 td, #table-1 th {
            text-align: center;
            padding: 5px 10px;
            font-size: 12px;
            font-family: Verdana;
            color: rgb(177, 106, 104);
        }
        #table-1 tr {
            background: #FFF
        }
        .types {
            background: rgb(238, 211, 210)
        }
        </style></head>
        <body><table id="table-1">
        """

        data = sqlhelper.status()

        for fd in data['flags_data']:
            res += """<tr><td colspan="%d" class='types'>%s(%d/%d)</td></tr>"""\
                   % (len(fd['data']) + 1, fd['flag'], fd['total_use'], data['proxy_num'])
            res += '<tr><th>成功率</th>'
            for d in fd['data']:
                res += """<td>%d%%</td>""" % d['succ_rate']
            res += '</tr><tr><th>代理数量</th>'
            for d in fd['data']:
                res += """<td>%d</td>""" % d['num']
            res += '</tr><tr><th>平均使用次数</th>'
            for d in fd['data']:
                res += """<td>%d</td>""" % d['avg_use_num']
            res += '</tr>'

        res += '</table></body></html>'
        self.write(res)


def start_api_server():
    """
    状态web
    :return:
    """

    init_tornado_log()

    # 默认配置
    define("port", default=API_PORT, help="run on the given port", type=int)

    tornado.options.parse_command_line()

    # 路由
    app = tornado.web.Application(handlers=[
        (r"/", StatusWeb),
        (r"/status", StatusWeb),
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
