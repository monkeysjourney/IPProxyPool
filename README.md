# IPProxyPool

## 项目介绍
ip代理池，fork自[https://github.com/qiyeboy/IPProxyPool](https://github.com/qiyeboy/IPProxyPool)

## 使用方法
1. 配置config文件，主要是 DB_CONFIG，数据库的配置
2. 启动爬取和接口服务，在文件IPProxy.py中
3. 通过接口调用。

## 接口介绍
默认端口号为8000，具体使用可参照[clientDemo](https://github.com/monkeysjourney/IPProxyPool/tree/master/clientDemo)。

1. / 或 /status: 查看使用状态
2. /get: 获取代理ip
3. /used: 反馈使用状况