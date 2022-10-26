# !/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from django.shortcuts import render

from django.views.decorators.http import require_POST, require_GET
from .models import ManagerUser, RechargePhoneBillRecord, BuyStockRecord, WithDrawalRecord, BankRechargeRecord, \
    TransferAccountsRecord, UserBankCard, BankUser
from utils.compute_md5 import get_md5_salt
from utils.check_login import check_login_redirect
from django.shortcuts import redirect

menu_list = ['充值记录', '提现记录', '转账记录', '所有银行卡记录', '话费充值记录', '股票购买记录', '所有app用户']
menu_type = ['recharge', 'with_drawal', 'transfer_accounts', 'cards', 'recharge_phone_bill', 'buy_stock',
             'all_app_user']
menu_path = [f'/manager/index/?type={row}' for row in menu_type]


def check_actived(index, _type):
    if menu_type[index] == _type:
        return 'actived'
    return ''


@require_GET
def login(request):
    return render(request, 'login.html', {'messages': []})


@require_GET
def register(request):
    return render(request, 'register.html', {'messages': []})


@require_GET
@check_login_redirect('/manager/login/')
def manager_index(request):
    account = request.session.get('account')
    _type = request.GET.get('type')
    content = {'account': account}
    if not _type or _type not in menu_type:
        _type = menu_type[0]
        content['menus'] = [
            {'value': row, 'actived': check_actived(index, _type), 'path': menu_path[index]} for index, row in
            enumerate(menu_list)
        ]
        content['type_zh'] = menu_list[0]
    else:
        content['menus'] = [
            {'value': row, 'actived': check_actived(index, _type), 'path': menu_path[index]} for
            index, row in
            enumerate(menu_list)
        ]
        content['type_zh'] = menu_list[menu_type.index(_type)]


    if _type == 'recharge':
        content['datas'] = [{'用户ID': row.user_id, '充值时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'), '充值金额': row.money,
                             '充值银行卡号': row.card_no, '充值后余额': row.balance, '用户账号': row.account,
                             '用户名': row.name, '用户手机号码': row.phone, '用户当前余额': row.lastest_money,
                             } for row in BankRechargeRecord.objects.raw(
            "select a.*, b.account,b.name,b.sex,b.phone,b.money as lastest_money from bank_bankrechargerecord a left join bank_bankuser b on a.user_id=b.id; "
        )]
    elif _type == 'with_drawal':
        content['datas'] = [
            {'用户ID': row.user_id, '提现时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'), '提现金额': row.money,
             '提现银行卡号': row.card_no, '提现后余额': row.balance, '用户账号': row.account,
             '用户名': row.name, '用户手机号码': row.phone, '用户当前余额': row.lastest_money,
             } for row in WithDrawalRecord.objects.raw(
                "select a.*, b.account,b.name,b.sex,b.phone,b.money as lastest_money from bank_withdrawalrecord a left join bank_bankuser b on a.user_id=b.id; "
            )]
    elif _type == 'transfer_accounts':
        content['datas'] = [
            {'用户ID': row.user_id, '转账时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'), '转账金额': row.money,
             '转账后余额': row.balance, '用户账号': row.account,
             '用户名': row.name, '用户手机号码': row.phone, '用户当前余额': row.lastest_money,
             '收款人名': row.payee_name, '收款人手机号码': row.payee_phone
             } for row in TransferAccountsRecord.objects.raw(
                "select a.*, b.account,b.name,b.sex,b.phone,b.money as lastest_money from bank_transferaccountsrecord a left join bank_bankuser b on a.user_id=b.id; "
            )]
    elif _type == 'cards':
        content['datas'] = [
            {'用户ID': row.user_id, '添加时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'),'银行卡号': row.card_no,
             '是否已删除': '已删除' if row.is_delete else '正常',
             '用户账号': row.account,
             '用户名': row.name, '用户手机号码': row.phone, '用户当前余额': row.lastest_money,
             } for row in UserBankCard.objects.raw(
                "select a.*, b.account,b.name,b.sex,b.phone,b.money as lastest_money from bank_userbankcard a left join bank_bankuser b on a.user_id=b.id "
            )]
    elif _type == 'recharge_phone_bill':
        content['datas'] = [
            {'用户ID': row.user_id, '充值话费时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'), '充值金额': row.pay_money,
             '充值人名': row.name,
             '充值话费后余额': row.balance, '用户账号': row.account,
             '用户名': row._name, '用户手机号码': row.phone, '用户当前余额': row.lastest_money,
             } for row in TransferAccountsRecord.objects.raw(
                "select a.*, b.account,b.name as _name,b.sex,b.phone,b.money as lastest_money from bank_rechargephonebillrecord a left join bank_bankuser b on a.user_id=b.id; "
            )]
    elif _type == 'buy_stock':
        content['datas'] = [
            {'用户ID': row.user_id, '购买股票时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'), '购买金额': row.money,
             '股票嗲吗': row.stock_number,
             '购买后余额': row.balance, '用户账号': row.account,
             '用户名': row._name, '用户手机号码': row.phone, '用户当前余额': row.lastest_money,
             } for row in TransferAccountsRecord.objects.raw(
                "select a.*, b.account,b.name as _name,b.sex,b.phone,b.money as lastest_money from bank_buystockrecord a left join bank_bankuser b on a.user_id=b.id; "
            )]
    elif _type == 'all_app_user':
        content['datas'] = [{
            '用户ID': row.id, '加入时间': row.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            '身份证号码': row.id_number, '账号': row.account, '实名用户': row.name, '性别': row.sex,
            '手机号码': row.phone, 'qx': row.qx, '用户当前余额': row.money, '编辑': 'edit'
        } for row in BankUser.objects.all()]
    content['keys'] = list(content['datas'][0].keys())
    print(content['menus'])
    return render(request, 'manager_base.html', content)


@require_POST
def login_handle(request):
    account = request.POST['inputAccount']
    password = request.POST['inputPassword']

    user = ManagerUser.objects.filter(account=account, password=get_md5_salt(password))
    if not user.exists():
        return render(request, 'login.html', {'messages': [{'value': '账号或密码不正确', 'alert': 'alert-warning'}]})
    request.session['is_login'] = 'true'
    request.session['account'] = account
    request.session['user_id'] = user[0].id
    return redirect('/manager/index/')


@require_POST
def register_handle(request):
    account = request.POST['inputAccount']
    password = request.POST['inputPassword']
    password_again = request.POST['inputPasswordAgain']

    if password != password_again:
        return render(request, 'register.html', {'messages': [{'value': '两次输入的密码不一致', 'alert': 'alert-warning'}]})
    if ManagerUser.objects.filter(account=account).exists():
        return render(request, 'register.html', {'messages': [{'value': '账号已存在！', 'alert': 'alert-warning'}]})
    user = ManagerUser.create(account, password)
    user.save()
    return render(request, 'login.html', {'messages': [{'value': '注册成功，请登录', 'alert': 'alert-success'}]})


@require_GET
def search_record(request):
    type = request.GET.get('type')
