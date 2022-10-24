import os

from django.db import models
import django.utils.timezone as timezone

from utils.compute_md5 import get_md5
from bank.default import DEFAULT_SALT

envget = os.environ.get


class BankUser(models.Model):
    id = models.AutoField(primary_key=True)
    id_number = models.CharField(max_length=18)
    account = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    sex = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    login_password = models.CharField(max_length=32)  # 密码hash后存储
    pay_password = models.CharField(max_length=32)
    qx = models.CharField(max_length=200)
    money = models.DecimalField(max_digits=12, decimal_places=2)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, id_number, account, name, sex, phone, login_password, pay_password, qx, money=0, **kwargs):
        user = cls(id_number=id_number, account=account, name=name, sex=sex, phone=phone,
                   login_password=get_md5(login_password + DEFAULT_SALT),
                   pay_password=get_md5(pay_password + DEFAULT_SALT),
                   qx=qx, money=money
                   )
        return user
