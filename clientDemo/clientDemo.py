# -*- coding:UTF-8 -*-

# 官方
import json
import time

# 第三方
import requests

# own
from util.log import logger
from config import get_header

PROXY_SERVER_ADDR = 'localhost'
PROXY_SERVER_PORT = 8000
PROXY_GET_ONCE_NUM = 30


class ProxyRequest:
    """
    代理
    """
    def __init__(self, use_flag='default'):
        """
        初始化
        """
        self.use_flag = use_flag
        self.proxies = []
        self.get_url = "http://%s:%d/get?count=%d&use_flag=%s" % \
                       (PROXY_SERVER_ADDR, PROXY_SERVER_PORT, PROXY_GET_ONCE_NUM, self.use_flag)
        self.used_url = "http://%s:%d/used" % (PROXY_SERVER_ADDR, PROXY_SERVER_PORT)

    def _get_proxy(self):
        """
        获取代理
        """
        req = requests.get(self.get_url)

        # 解析
        self.proxies += [{'proxy': '%s:%d' % (p[0], p[1]), 'id': p[2]}
                         for p in json.loads(req.text)]

        # 打印
        logger.info("get proxy success, now local num %d." % len(self.proxies))

    def _proxy_used(self, proxy_id, is_succ, speed):
        """
        代理使用反馈
        """
        req = requests.post(self.used_url, json.dumps({'id': proxy_id, 'is_succ': str(is_succ),
                                                       'speed': speed, 'use_flag': self.use_flag}
                                                      )
                            )

        if not req:
            logger.error('used post error, %s' % req)
        elif req.text.find('error') != -1:
            logger.error('Used post return error.')

    def request(self, url, encoding='utf-8', use_proxy=True):
        """
        获取页面
        :param url: url
        :param encoding: 编码
        :param use_proxy: 是否使用代理
        :return:
        """

        if use_proxy:
            if not self.proxies:
                self._get_proxy()
        proxy, proxy_id = self.proxies.pop()

        # 获取页面 一直获取 直到获取到
        while True:
            try:
                start = time.time()
                req = requests.get(url=url,
                                   headers=get_header(),
                                   timeout=(5, 10),  # 超时时间，(连接超时时间，读取超时时间)
                                   proxies={"http": proxy}
                                   )
                req.encoding = encoding

                if req.ok:
                    speed = round(time.time() - start, 2)
                    self._proxy_used(proxy_id, True, speed)
                    return req.text
                else:
                    self._proxy_used(proxy_id, False, 0)
                    return None
            except Exception as e:
                logger.exception(e)
                self._proxy_used(proxy_id, False, 0)
                return None

