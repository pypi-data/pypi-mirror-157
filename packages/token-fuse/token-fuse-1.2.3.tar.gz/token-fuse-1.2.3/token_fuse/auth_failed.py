class AuthFailed:
    """用于生成一个包含具体错误信息的布尔值为假的对象
    应用场景：当检查的token不合法时如果仅仅返回False，将无法了解该token的具体错误信息是什么，
    是被篡改还是已过期还是其它错误类型。AuthFailed(err_msg)生成的对象布尔值为False，同时包含了具体了错误信息"""

    def __init__(self, err_msg):
        """
        :param err_msg: 错误信息
        """
        self.__err_msg = err_msg

    def __bool__(self):
        return False

    def __str__(self):
        return self.__err_msg
