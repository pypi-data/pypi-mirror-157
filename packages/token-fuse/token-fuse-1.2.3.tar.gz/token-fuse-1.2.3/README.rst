一.生成和校验通用的token
~~~~~~~~~~~~~~~~~~~~~~~~

安装和引入Jwt模块
                 

::

    pip install token-fuse

    from token_fuse import Jwt

实例化
      

::

    jwt = Jwt() 

组织payload
           

::

    必选参数：
        1. exp 过期时间 ，now > exp 则失效
    可选参数：
        1. uid：用户辨识用户的唯一id，建议[uid, user]任选一种作为参数
        2. iss:签发人
        3. iat：签发时间戳

    payload = {'user': 'admin', 'iss': 'django', 'iat': 1642147838, 'exp': 1642152838}

生成token
         

::

    token = jwt.token(payload) 

校验token
         

::

    result = jwt.auth(token)

打印校验结果
            

    如校验成功返回payload，失败则返回一个布尔为False的AuthFailed对象，打印该对象可查看具体错误信息

::

    print(result) 

二. 生成和校验带“熔断”功能的token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在有些项目中，业务要求限制允许token登录的最大数量，本模块利用redis记录token，达到限制登录数量的目的。
引入JwtFuse模块

::

    from token_fuse import JwtFuse

配置Django setting.py
                     

::

    # 如果JWT_CONF缺省，max_login=1
    # redis=dict(host='127.0.0.1', port=6379, db=0)
    JWT_CONF = {
        'max_login': 3,
        'redis': dict(host='127.0.0.1', port=6379, db=0)
    }

实例化
      

::

    jwt_fuse = JwtFuse()

组织payload
           

::

    必选参数有: 
        1.exp 过期时间 ，now > exp 则失效
        2.iat：签发时间戳 。
        3.uid：用户辨识用户的唯一id，建议[uid, user]任选一种作为参数名都可以
    可选参数有：
        1.iss:签发人，在同一台服务器中如果存在多个项目（多项目共用了Redis数据池），
        如果这些项目不是共享token，那么在JwtRange().auth()时为了防止token串号，可以设置iss用于区分。

    payload = {'user': 'admin', 'iss': 'django', 'iat': 1642147838, 'exp': 1642152838}

生成token
         

    如果传入了request参数，则默认生成带有设备信息的token，
    然后根据request中的User-Agent将访问的请求区分为移动和PC两种设备类型。
    再将设备类型{'ua':'m'}或{'ua':'p'}更新到payload中，
    最后使用带有设备类型标记的payload生成token。
    不同设备类型不共享max\_login,也就是说max\_login=1时，ua:p和ua:m的设备能同时登录访问。

::

    token = jwt_fuse.token(payload, request=None) 

校验token
         

    校验通过的token会被保存在redis中，保存时间3600秒。保存格式：uid:[token1,token2...]，auth函数只会通过最新签发时间的max\_len条token.

::

    result = jwt_fuse.auth(token)

打印校验结果
            

    如校验成功返回payload，失败则返回一个布尔为False的AuthFailed对象，打印该对象可查看具体错误信息

::

    print(result)
