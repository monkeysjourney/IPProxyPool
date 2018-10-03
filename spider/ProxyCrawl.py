# coding:utf-8
import time
import gevent
import gevent.monkey
from gevent import monkey
monkey.patch_all()

from util.log import logger, init_log

from config import parserList, UPDATE_TIME, MAX_DOWNLOAD_CONCURRENT, MAX_CHECK_CONCURRENT_PER_PROCESS
from spider.HtmlDownloader import Html_Downloader
from spider.HtmlPraser import Html_Parser
from db.SqlHelper import SqlHelper as SqlHelper


def start_proxy_crawl():
    crawl = ProxyCrawl()
    crawl.run()


class ProxyCrawl(object):

    def __init__(self):
        self.sqlhelper = SqlHelper()
        # self.sqlhelper.init_db()

        self.proxies_set = set()
        self.url_count = 0
        self.url_total = sum([len(p['urls']) for p in parserList])

    def run(self):
        while True:
            self.proxies_set.clear()
            logger.info('------> loop begin')

            # TODO 删除无效代理
            logger.info('删除无效代理 %d 个。' % 0)

            # 现有代理列表 现有代理数量
            count = 0
            for proxy in self.sqlhelper.select_all():
                count += 1
                self.proxies_set.add('%s:%s' % (proxy[0], proxy[1]))
            begin_num = len(self.proxies_set)
            logger.info('现有代理数量 %d 个。' % begin_num)
            if begin_num != count:
                logger.error('数据库中存在重复代理 -- %d --> %d' % (count, begin_num))

            logger.info('爬取新的代理...')
            spawns = []
            self.url_count = 0
            for p in parserList:
                spawns.append(gevent.spawn(self.crawl, p))
                if len(spawns) >= MAX_DOWNLOAD_CONCURRENT:
                    gevent.joinall(spawns)
                    spawns = []
            gevent.joinall(spawns)
            spawns.clear()

            end_num = len(self.proxies_set)
            logger.info('新代理爬取完成，当前代理数量 %d, 新增加 %d!' % (end_num, end_num - begin_num))

            logger.info('------> loop end, sleep %ds!\n' % UPDATE_TIME)

            time.sleep(UPDATE_TIME)

    def crawl(self, parser):
        """
        爬取
        :param parser:
        :return:
        """
        html_parser = Html_Parser()
        for url in parser['urls']:
            response = Html_Downloader.download(url)
            if response is not None:
                proxy_list = html_parser.parse(response, parser)
                if proxy_list is not None:
                    # 检查爬取到的proxy
                    count, new = 0, 0
                    for proxy in proxy_list:
                        count += 1
                        proxy_str = '%s:%s' % (proxy['ip'], proxy['port'])
                        if proxy_str not in self.proxies_set:
                            self.proxies_set.add(proxy_str)
                            new += 1
                            self.sqlhelper.insert(proxy)
                    self.url_count += 1
                    logger.info('%d/%d -- <%s> 获取%d, 未记录的%d' %
                                (self.url_count, self.url_total, url, count, new))
                else:
                    self.url_count += 1
                    logger.warning('%d/%d -- <%s> 解析数据错误' % (self.url_count, self.url_total, url))
            else:
                self.url_count += 1
                logger.warning('%d/%d -- <%s> 下载页面错误' % (self.url_count, self.url_total, url))


if __name__ == "__main__":
    init_log()
    start_proxy_crawl()
