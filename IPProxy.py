# coding:utf-8

from multiprocessing import Process
from api.apiServer import start_api_server
from spider.ProxyCrawl import start_proxy_crawl

if __name__ == "__main__":
    p0 = Process(target=start_api_server)
    p1 = Process(target=start_proxy_crawl)
    p0.start()
    p1.start()
    p0.join()
    p1.join()
