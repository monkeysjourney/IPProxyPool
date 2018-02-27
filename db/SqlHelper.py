# coding:utf-8
import datetime
from sqlalchemy import Column, create_engine, VARCHAR, Integer, BigInteger, DateTime, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DB_CONFIG, DEFAULT_SELECT_LIMIT

'''
sql操作的基类
包括ip，端口，types类型(0高匿名，1透明)，protocol(0 http,1 https http),country(国家),area(省市),updatetime(更新时间)
 speed(连接速度)
'''

BaseModel = declarative_base()


class Proxy(BaseModel):
    __tablename__ = 'proxy'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(VARCHAR(16), nullable=False)
    port = Column(Integer, nullable=False)
    country = Column(VARCHAR(100), nullable=False)
    area = Column(VARCHAR(100), nullable=False)
    insert_at = Column(DateTime(), default=datetime.datetime.utcnow)


class ProxyUse(BaseModel):
    __tablename__ = 'proxy_use'
    id = Column(Integer, primary_key=True, autoincrement=True)
    use_flag = Column(VARCHAR(32), nullable=False, default='default')
    proxy_id = Column(Integer, nullable=False)
    use_num = Column(Integer, nullable=False, default=0)
    succ_num = Column(Integer, nullable=False, default=0)
    total_speed = Column(BigInteger, nullable=False, default=0)
    update_at = Column(DateTime(), default=datetime.datetime.now())


class SqlHelper:
    params = {'ip': Proxy.ip, 'port': Proxy.port, 'country': Proxy.country, 'area': Proxy.area}

    def __init__(self):
        if 'sqlite' in DB_CONFIG['DB_CONNECT_STRING']:
            connect_args = {'check_same_thread': False}
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False, connect_args=connect_args)
        else:
            self.engine = create_engine(DB_CONFIG['DB_CONNECT_STRING'], echo=False)
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()

        BaseModel.metadata.create_all(self.engine)

    def insert(self, value):
        """
        插入
        :param value:
        :return:
        """
        self.session.add(Proxy(ip=value['ip'], port=value['port'], country=value['country'], area=value['area']))
        self.session.commit()

    def delete(self):
        """
        删除
        :param conditions:
        :return:
        """
        pass

    def select_all(self):
        return self.session.query(Proxy.ip, Proxy.port).all()

    def update(self, proxy_id, is_succ, speed, use_flag='default'):
        """
        更新表格
        :param proxy_id: 代理的id
        :param is_succ: 是否成功
        :param speed: 花费时间
        :param use_flag: 使用标志
        :return:
        """
        if is_succ:
            succ_num = 1
        else:
            succ_num = 0

        query = self.session.query(ProxyUse.id) \
            .filter(ProxyUse.proxy_id == proxy_id) \
            .filter(ProxyUse.use_flag == use_flag)

        # 如果没有记录插入 如果有记录 更新
        if not query.one_or_none():
            self.session.add(
                ProxyUse(use_flag=use_flag, proxy_id=proxy_id, use_num=1, succ_num=succ_num, total_speed=speed))
        else:
            query.update({ProxyUse.use_num: ProxyUse.use_num + 1,
                          ProxyUse.succ_num: ProxyUse.succ_num + succ_num,
                          ProxyUse.total_speed: ProxyUse.total_speed + speed,
                          ProxyUse.update_at: datetime.datetime.now()})

        self.session.commit()

    def select(self, count=DEFAULT_SELECT_LIMIT, use_flag='default'):
        """
        获取代理
        首先返回没有使用过的，然后返回成功几率在50%以上、最近没有使用过的
        :param count:
        :param use_flag:
        :return:
        """
        query = self.session.query(Proxy.ip, Proxy.port, Proxy.id)
        # 1、查询当前use_flag未使用的代理 即id未在ProxyUse表中的数据
        res = query.filter(Proxy.id.notin_(self.session.query(ProxyUse.proxy_id).filter(ProxyUse.use_flag == use_flag))) \
            .limit(count) \
            .all()

        # 2、查询使用次数大于10次 成功几率在50%以上，或者小于10次 最近没有使用过的代理
        if len(res) < count:
            res += query.join(ProxyUse, Proxy.id == ProxyUse.proxy_id) \
                .filter(or_(ProxyUse.use_num < 10,
                            and_(ProxyUse.use_num > 10, ProxyUse.succ_num > ProxyUse.use_num / 2).self_group())) \
                .order_by(ProxyUse.update_at) \
                .limit(count - len(res)) \
                .all()
        return res

    def close(self):
        pass


if __name__ == '__main__':
    sqlhelper = SqlHelper()
    sqlhelper.update(3, True, 12, 'choice')
    print(sqlhelper.select())
