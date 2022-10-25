import os

from django.db import models
import django.utils.timezone as timezone

from utils.compute_md5 import get_md5_salt

envget = os.environ.get


class BankUser(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    id_number = models.CharField('身份证号码', max_length=18)
    account = models.CharField('账号', max_length=200)
    name = models.CharField('用户名', max_length=200)
    sex = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    login_password = models.CharField(max_length=32)  # 密码hash后存储
    pay_password = models.CharField(max_length=32)
    qx = models.CharField(max_length=200)
    money = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @classmethod
    def create(cls, id_number, account, name, sex, phone, login_password, pay_password, qx, money=0, **kwargs):
        user = cls(id_number=id_number, account=account, name=name, sex=sex, phone=phone,
                   login_password=get_md5_salt(login_password),
                   pay_password=get_md5_salt(pay_password),
                   qx=qx, money=money
                   )
        return user


class UserBankCard(models.Model):
    # 用户的银行卡表
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField('用户ID')
    card_no = models.CharField(max_length=100)
    is_delete = models.BooleanField('是否删除', default=False)


class BankRechargeRecord(models.Model):
    # 充值记录表
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField('用户ID')
    money = models.DecimalField('充值金额', max_digits=12, decimal_places=2)
    card_no = models.CharField(max_length=200)  # 本来这是和 UserBankCard 表相关联的
    balance = models.DecimalField('余额', max_digits=12, decimal_places=2)


class WithDrawalRecord(models.Model):
    # 提现记录表
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField('用户ID')
    money = models.DecimalField('提现金额', max_digits=12, decimal_places=2)
    card_no = models.CharField(max_length=200)  # 本来这是和 UserBankCard 表相关联的
    balance = models.DecimalField('余额', max_digits=12, decimal_places=2)


class TransferAccountsRecord(models.Model):
    # 转账记录表
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField('用户ID')
    payee_id = models.IntegerField('收款账户ID')
    payee_name = models.CharField(max_length=200)
    payee_phone = models.CharField(max_length=200)
    money = models.DecimalField('转账金额', max_digits=12, decimal_places=2)
    balance = models.DecimalField('余额', max_digits=12, decimal_places=2)


class RechargePhoneBillRecord(models.Model):
    # 话费充值记录表
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField('用户ID')
    name = models.CharField('用户名', max_length=200)
    pay_money = models.DecimalField('充值金额', max_digits=12, decimal_places=2)
    balance = models.DecimalField('余额', max_digits=12, decimal_places=2)


class BuyStockRecord(models.Model):
    id = models.AutoField(primary_key=True)
    create_time = models.DateTimeField(default=timezone.now)
    update_time = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField('用户ID')
    money = models.DecimalField('购买金额', max_digits=12, decimal_places=2)
    stock_number = models.CharField('股票编号，也就是股票代码', max_length=200)
    balance = models.DecimalField('购买后，账户余额', max_digits=12, decimal_places=2)
