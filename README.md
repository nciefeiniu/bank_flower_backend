# 手机app的后端项目以及网页版
> python 3.7 + mysql 8

推荐使用 [PyCharm](https://www.jetbrains.com/pycharm/) 启动

安卓手机使用的是 `bank/api/` 的URL

网页管理端使用的是 `manager/` 的URL


## 怎么启动

1. 修改数据库配置信息，在 `bank_of_flower/settings.py` 这个文件中修改如下的配置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bank_of_flower',  # 数据库名。注意，请自己手动在数据库中创建一个名为这个的数据库
        'USER': 'django_app',  # 账号
        'PASSWORD': '123456',  # 密码
        'HOST': '127.0.0.1',  # HOST
        'POST': 3306,  # 端口
    }
}
```

2. 安装所需的依赖
```bash
pip install -r requirements.txt
```

3. 同步数据库
```
python manage.py makemigrations
python manage.py migrate
```

4. 启动服务
```
python manage.py runserver 0.0.0.0:8081
```

5. 用浏览器打开连接 [http://127.0.0.1:8081/manager/index/](http://127.0.0.1:8081/manager/index/)


## 启动后

1. 网页端通过 [http://127.0.0.1:8081/manager/index/](http://127.0.0.1:8081/manager/index/) 这个连接打开即可

2. 安卓手机端请修改 `com/example/phonewallet11/ApiBaseUrl.java` 文件里面的服务地址。
注意，因为安卓手机和PC不是一个环境，接口地址肯定不是 http://127.0.0.1
应该修改为你电脑从路由器上获取的IP地址，比如 http://192.168.3.1


## 功能简介

1. 管理员的登录注册
2. 查看所有安卓端账号，可以修改安卓端账号信息，可以拉黑安卓账号
3. 查看所有充值记录
4. 查看所有提现记录
5. 查看所有转账记录
6. 查看安卓端用户添加的所有银行卡
7. 查看所有话费充值记录
8. 查看所有股票购买记录