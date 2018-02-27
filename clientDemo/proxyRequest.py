# -*- coding:UTF-8 -*-

# 官方
import json
import time
import random

# 第三方
import requests

# own
from util.log import logger

# 请求头 浏览器类型库
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
]


class ProxyRequest:
    """
    代理
    """

    def __init__(self, addr, port, once_get_num=30, use_flag='default'):
        """
        初始化
        """
        self.use_flag = use_flag
        self.proxies = []
        self.get_url = "http://%s:%d/get?count=%d&use_flag=%s" % \
                       (addr, port, once_get_num, self.use_flag)
        self.used_url = "http://%s:%d/used" % (addr, port)
        self._get_proxy()

    def _get_proxy(self):
        """
        获取代理
        """
        req = requests.get(self.get_url)

        datas = [('%s:%d' % (p[0], p[1]), p[2]) for p in json.loads(req.text)]

        # 多个线程会同时调用回去接口 导致获取的数据完全相同
        if not self.proxies:
            self.proxies += datas
            # 打印
            logger.info("Get proxy success, now local num %d." % len(self.proxies))

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

    def get(self, url, validator_func, encoding='utf-8', use_proxy=True):
        """
        获取页面 并检测内容
        :param url: url
        :param validator_func: 内容检测函数
        :param encoding: 编码
        :param use_proxy: 是否使用代理
        :return:
        """
        id = url.replace("http://app.jg.eastmoney.com/NewsData/GetNewsText.do?id=", "")\
            .replace("&cid=3948045045460666", '')\
            .replace("http://app.jg.eastmoney.com/Notice/GetNoticeText.do?id=", "")\
            .replace("&cid=3948047684990666", '')

        # 获取页面 一直获取 直到获取到 或者获取了30次
        for i in range(100):
            if use_proxy:
                if not self.proxies:
                    self._get_proxy()
            proxy, proxy_id = self.proxies.pop()

            logger.info('%s -- proxy with %s' % (id, proxy))

            try:
                start = time.time()
                req = requests.get(url=url,
                                   headers={'User-Agent': random.choice(USER_AGENTS),
                                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                            'Accept-Language': 'en-US,en;q=0.5',
                                            'Connection': 'keep-alive',
                                            'Accept-Encoding': 'gzip, deflate',
                                            },
                                   timeout=(5, 10),  # 超时时间，(连接超时时间，读取超时时间)
                                   proxies={"http": proxy}
                                   )
                req.encoding = encoding

                if req.ok:
                    speed = round(time.time() - start, 2)
                    # 解析内容
                    data = validator_func(req.text)
                    if data:
                        # 反馈
                        self._proxy_used(proxy_id, True, speed)
                        # 返回
                        return data
                else:
                    # logger.info('request error -- %s' % req)
                    pass
            except Exception as e:
                # logger.error(e)
                pass

            # logger.info('%s get error, continue, now num is %d' % (id, i))
            self._proxy_used(proxy_id, False, 0)
