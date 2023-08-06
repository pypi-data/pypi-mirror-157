import hmac
import base64


class Encryption:
    """加密类"""

    def to_bytes(self, bytes_or_str):
        if isinstance(bytes_or_str, str):
            value = bytes_or_str.encode('utf-8')
        else:
            value = bytes_or_str
        return value

    def to_str(self, bytes_or_str):
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')
        else:
            value = bytes_or_str
        return value

    def base64(self, content, alt_chars=None):
        """base64编码
        :param content:需要编码的内容
        为了生成安全的Base64字符串会把结尾的“==”号去掉。
        :param alt_chars:可选的alt_chars是长度为2的字节字符串（推荐：alt_chars="-_"），
        指定“+”和“/”字符的替换字符，用于生成安全的Base64字符串“+” 替换为 “-”，“/” 替换为 ""_"" ,也可以为None
        :return:base64编码的数据，一般为字符串类型
        """
        content = self.to_bytes(content)
        alt_chars = self.to_bytes(alt_chars) if alt_chars else alt_chars
        content_base64 = base64.b64encode(content, altchars=alt_chars)
        return content_base64.decode('utf-8').replace('=', '')

    def debase64(self, content: str, is_string=True, alt_chars=None):
        """base64解码
        :param content:需要解码的内容，一般为字符串类型，
        base64数据长度应为4的整数倍，如果长度取模后的余数不等于0，那么需要补齐的“=”号的个数为4减去取模后的余数。
        :param is_string:解码结果的期待数据类型是否为字符串，is_string=True时编码结果会decode()成字符串。
        如果是图片这里需要is_string=False以返回bytes
        :param alt_chars:可选的alt_chars是长度为2的字节字符串（一般为：alt_chars="-_"），
        需要解码的内容如果是安全的Base64字符串,需要指定“+”和“/”字符的替换字符。
        :return:ase64解码的数据
        """
        num = len(content) % 4  # content长度取模后的余数
        content = content + '=' * (4 - num) if num else content  # 补齐“=”号，个数为4减去余数
        content = self.to_bytes(content)
        alt_chars = self.to_bytes(alt_chars) if alt_chars else alt_chars
        content = base64.b64decode(content, altchars=alt_chars)
        return content.decode('utf-8') if is_string else content

    def hmac_sha(self, key, message, digest_mod='sha256'):
        """
        hmac.SHA 加密
        :param key: 密钥
        :param message:加密内容 bytes
        :param digest_mod:加密类型 sha256 或者 sha1等
        :return:密文 base64格式的密文
        """
        key = self.to_bytes(key)
        message = self.to_bytes(message)
        h = hmac.new(key, message, digestmod=digest_mod)
        return self.base64(h.digest(), alt_chars="-_")


if __name__ == '__main__':
    print(Encryption().hmac_sha('secret', 'Hello world'))
