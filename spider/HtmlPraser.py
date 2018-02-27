# coding:utf-8
import base64
from config import QQWRY_PATH, CHINA_AREA
from util.IPAddress import IPAddresss
import re
from util.compatibility import text_

from lxml import etree


class Html_Parser(object):
    def __init__(self):
        self.ips = IPAddresss(QQWRY_PATH)

    def parse(self, response, parser):
        """
        :param response: 响应
        :param type: 解析方式
        :return:
        """
        if parser['type'] == 'xpath':
            return self.XpathPraser(response, parser)
        elif parser['type'] == 'regular':
            return self.RegularPraser(response, parser)
        elif parser['type'] == 'module':
            return getattr(self, parser['moduleName'], None)(response, parser)
        else:
            return None

    @staticmethod
    def auth_country(addr):
        """
        用来判断地址是哪个国家的
        :param addr:
        :return:
        """
        for area in CHINA_AREA:
            if text_(area) in addr:
                return True
        return False

    def parse_ip_to_addr(self, ip):
        addr = self.ips.getIpAddr(self.ips.str2ip(ip))

        country = ''
        area = ''

        if '省' in addr or self.auth_country(addr):
            country = text_('国内')
            area = addr
        else:
            country = text_('国外')
            area = addr

        return country, area

    def XpathPraser(self, response, parser):
        """
        针对xpath方式进行解析
        :param response:
        :param parser:
        :return:
        """
        proxy_list = []
        root = etree.HTML(response)
        proxies = root.xpath(parser['pattern'])
        for proxy in proxies:
            try:
                ip = proxy.xpath(parser['position']['ip'])[0].text
                port = proxy.xpath(parser['position']['port'])[0].text
                country, area = self.parse_ip_to_addr(ip)
            except Exception as e:
                continue

            proxy = {'ip': ip, 'port': int(port), 'country': country, 'area': area}
            proxy_list.append(proxy)
        return proxy_list

    def RegularPraser(self, response, parser):
        """
        针对正则表达式进行解析
        :param response:
        :param parser:
        :return:
        """
        proxy_list = []
        pattern = re.compile(parser['pattern'])
        matches = pattern.findall(response)
        if matches is not None:
            for match in matches:
                try:
                    ip = match[parser['position']['ip']]
                    port = match[parser['position']['port']]
                    country, area = self.parse_ip_to_addr(ip)
                except Exception as e:
                    continue

                proxy = {'ip': ip, 'port': port, 'country': country, 'area': area}

                proxy_list.append(proxy)
            return proxy_list


    def CnproxyPraser(self, response, parser):
        """
        :param response:
        :param parser:
        :return:
        """
        proxy_list = self.RegularPraser(response, parser)
        char_dict = {'v': '3', 'm': '4', 'a': '2', 'l': '9', 'q': '0', 'b': '5', 'i': '7', 'w': '6', 'r': '8', 'c': '1'}

        for proxy in proxy_list:
            port = proxy['port']
            new_port = ''
            for i in range(len(port)):
                if port[i] != '+':
                    new_port += char_dict[port[i]]
            proxy['port'] = int(new_port)
        return proxy_list

    def proxy_listPraser(self, response, parser):
        proxy_list = []
        pattern = re.compile(parser['pattern'])
        matches = pattern.findall(response)
        if matches:
            for match in matches:
                try:
                    ip_port = base64.b64decode(match.replace("Proxy('", "").replace("')", ""))
                    ip = ip_port.split(':')[0]
                    port = ip_port.split(':')[1]
                    country, area = self.parse_ip_to_addr(ip)
                except Exception as e:
                    continue
                proxy = {'ip': ip, 'port': int(port), 'country': country, 'area': area}
                proxy_list.append(proxy)
            return proxy_list







