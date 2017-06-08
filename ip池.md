# ip池，定时更新
 IP池分两部分:

 1. key=ips 有100个IP的列表，ip有一定的不稳定性

 2. key=proxy 稳定的代理IP，目前有两个

## redis数据库配置
* 配置写在setting文件中
* master = 1192.168.1.25
```
REDIS_URL = 'redis://master:6379'
```

## Middleware中间件代码
```
class CustomHttpProxyMiddleware(object):
    def __init__(self):
        self.db = RedisDatabase()
        self.proxy = self.db.load("proxy")
        self.proxy_password = self.db.load("password")

    def process_request(self, request, spider):
        ips = self.db.load("ips") or self.proxy
        if ips:
            ip = random.choice(ips)
            print(ip)
            request.meta['proxy'] = "http://" + ip
            proxy_user_pass = self.proxy_password
            encode_user_pass = base64.b64encode(proxy_user_pass.encode()).decode()
            request.headers['Proxy-Authorization'] = 'Basic ' + encode_user_pass
```

## Redis数据库代码
```
class RedisDatabase(metaclass=Singleton):
    def __init__(self):
        self.conn = self._redis_conn()

    def _redis_conn(self):
        conn = redis.StrictRedis.from_url(settings.get("REDIS_URL"))
        return conn

    def dump(self, key, data):
        s = json.dumps(data)
        self.conn.set(key, s)

    def load(self, key):
        s = self.conn.get(key)
        if s:
            return json.loads(s)
```