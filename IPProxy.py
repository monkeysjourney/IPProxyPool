# coding:utf-8

from multiprocessing import Process
from api.apiServer import start_api_server

from spider.ProxyCrawl import start_proxy_crawl

from util.log import init_log

if __name__ == "__main__":
    init_log('ip_proxy')
    p0 = Process(target=start_api_server)
    p1 = Process(target=start_proxy_crawl)
    p0.start()
    p1.start()
    p0.join()
    p1.join()