import json
import heapq
import redis
from .json_web_token import JsonWebToken
from .auth_failed import AuthFailed
from django.conf import settings

JWT_CONF = getattr(settings, 'JWT_CONF', {})
MAX_LOGIN = JWT_CONF.get('max_login', 1)
REDIS_POOL = JWT_CONF.get('redis_pool') or redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
rds = redis.Redis(connection_pool=REDIS_POOL)


class JsonWebTokenFuse(JsonWebToken):

    def token(self, payload: dict):
        """根据payload生成token，
        :param payload:
            必选参数有: 1.exp 过期时间 ，now > exp 则失效
                      2.iat：签发时间戳 。
                      3.uid：用于辨识用户的唯一id，建议[uid, user]任选一种作为参数名都可以
            可选参数有：
                      1.iss:签发人，在同一台服务器中如果存在多个项目（多项目共用了Redis数据池），
                      如果这些项目不是共享token，那么在JwtFuse().auth()时为了防止token串号，可以设置iss用于区分。
        :return: 生成的token"""

        if 'iat' not in payload:
            raise ValueError('payload中不存在iat(签发时间)！')

        return super().token(payload=payload)

    def _generate_key(self, payload: dict):
        """生成token在Redis中的键名"""
        uid = payload.get('uid') or payload.get('user')  # 用户表示在payload中为user或uid
        if not uid:
            raise TypeError('payload中没有配置uid或user')
        iss = payload.get('iss') or 'no_iss'  # 如果没有指定签发人 则把iss默认为'no_iss'
        token_key = 'token:' + iss + ':' + str(uid)  # token在Redis中的键名
        return token_key

    def _push_token(self, tokens: list, token: str) -> list:
        """
        将token push到tokens中，如果tokens的长度超出max_len会pop掉时间最久的那条token
        :param tokens:一个保存token的list
        :param token:push的token，不一定保证push成功，这是因为如果该条token时间久远，在存入后即会被pop掉
        :return:tokens
        """
        _, payload, *_ = token.split('.')
        payload = json.loads(self.enc.debase64(payload, alt_chars='-_'))
        token_item = (payload['iat'], token)  # iat签发时间

        if token_item not in tokens:
            heapq.heappush(tokens, token_item)

        if len(tokens) > MAX_LOGIN:
            heapq.heappop(tokens)

        return tokens

    def auth(self, token: str):
        """验证token 只允许max_len条token有效"""
        payload = super().auth(token)
        if not payload:  # 如果token没有验证通过，返回payload（此时payload为AuthFailed()对象）
            return payload

        token_key = self._generate_key(payload)  # 生成token在Redis中的键名

        tokens = rds.get(token_key)  # 从redis中取出来的是bytes
        tokens = json.loads(tokens.decode('utf-8')) if tokens else []  # decode后转化成列表
        tokens = [tuple(i) for i in tokens]  # [[time,token],]-> [(time,token),],因为json后元组变成了列表
        tokens = self._push_token(tokens, token)  # token push to tokens
        # 存入redis的过期时间为3600秒 意味着3600秒后该token可以正常访问
        rds.set(token_key, json.dumps(tokens), 3600)
        if token in [i[-1] for i in tokens]:
            return payload
        else:
            return AuthFailed('token超出允许的数量范围')  # 103: token超出允许的数量范围
