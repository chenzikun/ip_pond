import requests
import redis
import json
import threading
from datetime import datetime

from config import PROXY_API
from config import REDIS_URL
from config import PROXY
from config import PROXY_USER_PASSWORD


def date_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class IpPond():
    def __init__(self):
        print("初始化IP池:", date_time())
        self.url = PROXY_API
        self.redis_db = RedisDatabase()

    def get_ips(self):
        print("提取ip:", date_time())
        data = requests.get(self.url).json()
        ips = data.get("data").get("proxy_list") or []
        self.redis_db.refresh(ips)


class RedisDatabase(object):
    def __init__(self):
        self.dump("ips", [])
        self.load_private_proxy(PROXY)
        self.load_proxy_password(PROXY_USER_PASSWORD)

    def _redis_conn(self):
        redis_conn = redis.StrictRedis.from_url(REDIS_URL)
        return redis_conn

    def dump(self, key, value):
        s = json.dumps(value)
        self._redis_conn().set(key, s)

    def refresh(self, data):
        self._redis_conn().delete('ips')
        self.dump("ips", data)

    def load_private_proxy(self, data):
        self.dump("proxy", data)

    def load_proxy_password(self, data):
        self.dump("password", data)


if __name__ == '__main__':
    ip_pond = IpPond()
    ip_pond.get_ips()
    while True:
        timer = threading.Timer(150, ip_pond.get_ips)
        timer.start()
        timer.join()
