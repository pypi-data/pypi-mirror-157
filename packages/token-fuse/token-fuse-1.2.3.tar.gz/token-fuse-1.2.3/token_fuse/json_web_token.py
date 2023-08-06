import json
import time

from .encryption import Encryption
from .auth_failed import AuthFailed
from django.conf import settings

SECRET_KEY = settings.SECRET_KEY


class JsonWebToken:
    def __init__(self):
        self.__header = json.dumps({"alg": "HS256", "typ": "JWT"})
        self.enc = Encryption()  # 加密类

    def _signature(self, header, payload):
        """注意这里的header和payload是base64编码之后的内容;"""
        signature = header + '.' + payload
        signature = self.enc.hmac_sha(SECRET_KEY, signature, digest_mod='sha256')
        return signature

    def token(self, payload: dict):
        """根据payload生成token，
        :param payload:
            必选参数有: 1.exp 过期时间 ，now > exp 则失效
                      2.uid：用户辨识用户的唯一id，建议[uid, user]任选一种作为参数名都可以
            可选参数有: 1.iss:签发人，
                      2.iat：签发时间戳 。
        :return: 生成的token
        """
        if 'exp' not in payload:
            raise ValueError('payload中不存在exp!')

        if 'uid' not in payload and 'user' not in payload:
            raise ValueError('payload中不存在uid(或user)！')

        payload = json.dumps(payload)  # 将payload从dict转为str
        header = self.enc.base64(self.__header, alt_chars='-_')  # base64加密header
        payload = self.enc.base64(payload, alt_chars='-_')  # 计算签名后才能将payload转换成base64
        signature = self._signature(header, payload)  # 计算签名
        token = header + '.' + payload + '.' + signature
        return token

    def auth(self, token: str):
        """
        验证token的合法性,这里只是验证token是否合法以及是否过期；
        :param token:待验证的token,exp(到期时间戳)是payload中的必选参数
        :return:token如果成功返回payload, 否则返回AuthFailed()的实例
        """
        try:
            header, payload, signature, *_ = token.split('.')
        except ValueError:
            return AuthFailed('token格式错误！应为：Header.Payload.Signature.')

        auth_sign = self._signature(header, payload)  # 用token中的header和payload生成签名
        if not auth_sign == signature:  # 如果token中header,payload与签名不符说明被篡改
            return AuthFailed('signature校验不通过，token不合法或者被篡改！')

        try:
            payload = json.loads(self.enc.debase64(payload, alt_chars='-_'))
        except Exception:
            return AuthFailed('payload部分格式错误！应该是一个被base64加密后的对象.')

        exp = payload['exp']  # 过期时间
        if int(time.time()) > exp:  # 30d=2592000s 90d=7776000s 是否到期
            return AuthFailed('token已经过期')  # 102: token已经过期
        return payload
