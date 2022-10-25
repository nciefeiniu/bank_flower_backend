from django.shortcuts import render

# Create your views here.

import json
import logging
import decimal

from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.contrib.auth.decorators import login_required

from bank.models import BankUser, BankRechargeRecord, WithDrawalRecord, TransferAccountsRecord, \
    UserBankCard, RechargePhoneBillRecord, BuyStockRecord
from bank.default import API_RESPONSE_FORMAT
from utils.compute_md5 import get_md5_salt


logger = logging.getLogger(__name__)


def get_model_fields(model) -> list:
    fields = [field.name for field in model._meta.get_fields()]
    return fields


def check_login(fn):
    def wrapper(request,*args,**kwargs):
        if request.session.get('is_login', 'false') == 'true':
            return fn(request,*args,*kwargs)
        else:
            response = HttpResponse('')
            response.status_code = 555  # 555 需要登录
            return response
    return wrapper


@require_POST
def register_account(request):
    # 注册账号
    resp_data = API_RESPONSE_FORMAT.copy()

    body_dict = json.loads(request.body)
    body_dict.update({
        'id_number': body_dict.get('_id')
    })
    for key in get_model_fields(BankUser):
        if key in ('id', 'create_time', 'update_time'):
            continue
        if not body_dict.get(key):
            resp_data.update({'message': f'{key} can not be empty!', 'success': False, 'code': 501})  # 数据提交不全
            return JsonResponse(resp_data)

    if BankUser.objects.filter(account=body_dict['account']).exists():
        resp_data.update({'message': f'账号已存在', 'success': False, 'code': '601',
                          'data': {}})

    if BankUser.objects.filter(id_number=body_dict['id_number']).exists():
        resp_data.update({'message': f'该身份证号码已注册过账号！', 'success': False, 'code': '602',
                          'data': {}})
        return JsonResponse(resp_data)

    user = BankUser.create(**body_dict)
    user.save()
    resp_data.update({'message': '注册成功，请登录',
                      'data': model_to_dict(user, ['id', 'account', 'name', 'sex', 'money'])})
    return JsonResponse(resp_data)


@require_GET
def check_account_exists(request):
    resp_data = API_RESPONSE_FORMAT.copy()

    account = request.GET.get('account')
    logger.debug(f'account: {account}')
    if not account:
        resp_data.update({'message': 'account can not be empty!', 'success': False})
        return JsonResponse(resp_data)
    user = BankUser.objects.filter(account=account)
    if user.exists():
        resp_data.update({'message': f'{account} exists!', 'data': {'exists': True}})
        return JsonResponse(resp_data)
    resp_data.update({'message': f'{account} not exists!', 'data': {'exists': False}})
    return JsonResponse(resp_data)


@require_POST
def login(request):
    # 登录账号
    resp_data = API_RESPONSE_FORMAT.copy()

    body_dict = json.loads(request.body)  # 传递的是 account 和 login_password
    account = body_dict.get('account')
    password = body_dict.get('login_password')
    if not account or not password:
        resp_data.update({'message': 'account or password can not be empty!', 'success': False, 'code': 501})
        return JsonResponse(resp_data)
    if not BankUser.objects.filter(account=account).exists():
        resp_data.update({'message': '账号不存在，请注册', 'success': False, 'code': 502})  # 账户不存在
        return JsonResponse(resp_data)
    password_md5 = get_md5_salt(password)
    if not BankUser.objects.filter(account=account, login_password=password_md5):
        resp_data.update({'message': '账号或密码错误，请重新输入', 'success': False, 'code': 503})  # 账户密码不匹配
        return JsonResponse(resp_data)
    user = BankUser.objects.get(account=account)
    request.session['is_login'] = 'true'
    request.session['account'] = account
    request.session['user_id'] = user.id
    resp_data.update({'message': '登录成功', 'success': True, 'data': {
        'account': account,
        'name': user.name,
        'sex': user.sex,
        'phone': user.phone,
        'moneys': float(user.money),
        'id': user.id,
        'id_number': user.id_number,
        'qx': user.qx
    }})
    return JsonResponse(resp_data)


@require_POST
@check_login
def recharge(request):
    # 充值接口
    resp_data = API_RESPONSE_FORMAT.copy()

    body_dict = json.loads(request.body)  # 传递的是 money 和 pay_password 和 card_no
    user_id = request.session.get('user_id')
    money = body_dict.get('money')
    pay_password = body_dict.get('pay_password')
    card_no = body_dict.get('card_no')

    if not money or not pay_password or not card_no:
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)
    if not UserBankCard.objects.filter(user_id=user_id, card_no=card_no).exists():
        resp_data.update({'message': '卡号不存在，请重新输入', 'success': False, 'code': 504})  # 卡号不存在
        return JsonResponse(resp_data)
    if not BankUser.objects.filter(id=user_id, pay_password=get_md5_salt(pay_password)).exists():
        resp_data.update({'message': '支付密码错误，请重新输入', 'success': False, 'code': 503})  # 账户密码不匹配
        return JsonResponse(resp_data)

    with transaction.atomic():
        user = BankUser.objects.get(id=user_id)
        user.money += decimal.Decimal(money)
        user.save()
        record = BankRechargeRecord(money=money, card_no=card_no, user_id=user_id, balance=user.money)
        record.save()
    resp_data.update({'message': 'ok', 'success': True})
    return JsonResponse(resp_data)


@check_login
@require_POST
def with_drawal(request):
    # 提现接口
    resp_data = API_RESPONSE_FORMAT.copy()

    body_dict = json.loads(request.body)  # 传递的是 money 和 pay_password 和 card_no
    user_id = request.session.get('user_id')
    money = body_dict.get('money')  # 提现金额
    pay_password = body_dict.get('pay_password')
    card_no = body_dict.get('card_no')  # 银行卡号

    if not money or not pay_password or not card_no:
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)
    if not UserBankCard.objects.filter(user_id=user_id, card_no=card_no).exists():
        resp_data.update({'message': '卡号不存在，请重新输入', 'success': False, 'code': 504})  # 卡号不存在
        return JsonResponse(resp_data)
    if not BankUser.objects.filter(id=user_id, pay_password=get_md5_salt(pay_password)).exists():
        resp_data.update({'message': '支付密码错误，请重新输入', 'success': False, 'code': 503})  # 账户密码不匹配
        return JsonResponse(resp_data)

    if float(BankUser.objects.get(id=user_id).money) < float(money):
        resp_data.update({'message': '余额不足', 'success': False, 'code': 510})  # 余额不足
        return JsonResponse(resp_data)

    with transaction.atomic():
        user = BankUser.objects.get(id=user_id)
        user.money -= decimal.Decimal(money)
        user.save()
        record = WithDrawalRecord(money=money, card_no=card_no, user_id=user_id, balance=user.money)
        record.save()
    resp_data.update({'message': 'ok', 'success': True})
    return JsonResponse(resp_data)


@check_login
@require_POST
def transfer_accounts(request):
    # 转账接口
    resp_data = API_RESPONSE_FORMAT.copy()

    body_dict = json.loads(request.body)  # 传递的是 money 和 name 和 phone 和 pay_password
    user_id = request.session.get('user_id')
    money = body_dict.get('money')  # 转账金额
    name = body_dict.get('name')  # 收款人名
    phone = body_dict.get('phone')  # 收款人手机
    pay_password = body_dict.get('pay_password')

    if not money or not pay_password or not name or not phone:
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)
    if not BankUser.objects.filter(id=user_id, pay_password=get_md5_salt(pay_password)).exists():
        resp_data.update({'message': '支付密码错误，请重新输入', 'success': False, 'code': 503})  # 账户密码不匹配
        return JsonResponse(resp_data)
    if not BankUser.objects.filter(name=name, phone=phone).exists():
        resp_data.update({'message': '对方账户不存在', 'success': False, 'code': 505})  # 对方账户不存在
        return JsonResponse(resp_data)

    payee = BankUser.objects.get(name=name, phone=phone)

    with transaction.atomic():
        user = BankUser.objects.get(id=user_id)
        user.money -= decimal.Decimal(money)
        user.save()
        record = TransferAccountsRecord(money=money, balance=user.money, payee_name=name, payee_phone=phone,
                                        payee_id=payee.id
                                        )
        record.save()
        payee.money += money
        payee.save()
    resp_data.update({'message': 'ok', 'success': True})
    return JsonResponse(resp_data)


@check_login
@require_POST
def add_card(request):
    # 添加银行卡
    resp_data = API_RESPONSE_FORMAT.copy()

    user_id = request.session.get('user_id')

    body_dict = json.loads(request.body)  # 传递的是 card_no，id_number

    card_no = body_dict.get('card_no')
    id_number = body_dict.get('id_number')
    if not card_no or not id_number:
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)
    user = BankUser.objects.get(id=user_id)
    if user.id_number != id_number:
        resp_data.update({'message': '身份证号码错误', 'success': False, 'code': 506})  # 身份证号码不正确
        return JsonResponse(resp_data)

    if UserBankCard.objects.filter(user_id=user_id, card_no=card_no).exists():
        resp_data.update({'message': '该银行卡已存在！', 'success': False, 'code': 508})  # 银行卡重复
        return JsonResponse(resp_data)

    card = UserBankCard(user_id=user_id, card_no=card_no)
    card.save()
    resp_data.update({'message': 'ok'})
    return JsonResponse(resp_data)


@check_login
@require_POST
def recharge_phone_bill(request):
    # 充话费
    resp_data = API_RESPONSE_FORMAT.copy()

    user_id = request.session.get('user_id')

    body_dict = json.loads(request.body)  # name, money, pay_password
    name = body_dict.get('name')
    money = body_dict.get('money')
    pay_password = body_dict.get('pay_password')

    if not name or not money or not pay_password:
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)

    if not BankUser.objects.filter(id=user_id, pay_password=get_md5_salt(pay_password)).exists():
        resp_data.update({'message': '支付密码错误，请重新输入', 'success': False, 'code': 503})  # 账户密码不匹配
        return JsonResponse(resp_data)

    if not BankUser.objects.filter(id=user_id, name=name).exists():
        resp_data.update({'message': '用户名错误，请重新输入', 'success': False, 'code': 507})  # 用户名错误
        return JsonResponse(resp_data)

    with transaction.atomic():
        user = BankUser.objects.get(id=user_id)
        user.money -= decimal.Decimal(money)
        user.save()
        record = RechargePhoneBillRecord(user_id=user_id, name=name, pay_money=money, balance=user.money)
        record.save()
    resp_data.update({'message': 'ok'})
    return JsonResponse(resp_data)


@check_login
@require_POST
def buy_stock(request):
    # 购买股票
    resp_data = API_RESPONSE_FORMAT.copy()

    user_id = request.session.get('user_id')

    body_dict = json.loads(request.body)  # money， stock_number, pay_password
    money = body_dict.get('money')
    stock_number = body_dict.get('stock_number')
    pay_password = body_dict.get('pay_password')

    if not stock_number or not money or not pay_password:
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)

    if not BankUser.objects.filter(id=user_id, pay_password=get_md5_salt(pay_password)).exists():
        resp_data.update({'message': '支付密码错误，请重新输入', 'success': False, 'code': 503})  # 账户密码不匹配
        return JsonResponse(resp_data)

    with transaction.atomic():
        user = BankUser.objects.get(id=user_id)
        user.money -= decimal.Decimal(money)
        user.save()
        record = BuyStockRecord(user_id=user_id, stock_number=stock_number, money=money, balance=user.money)
        record.save()
    return JsonResponse(resp_data)


@check_login
@require_GET
def get_all_card(request):
    # 获取所有银行卡
    user_id = request.session.get('user_id')
    cards = UserBankCard.objects.filter(user_id=user_id)
    resp_data = API_RESPONSE_FORMAT.copy()

    resp_data.update({'message': '', 'data': [
        {'card_no': card.card_no} for card in cards.all()
    ]})
    return JsonResponse(resp_data)


@check_login
@require_GET
def del_card(request):
    # 获取所有银行卡
    user_id = request.session.get('user_id')
    card_no = request.GET.get('card_no')
    resp_data = API_RESPONSE_FORMAT.copy()

    if not user_id or not card_no :
        resp_data.update({'message': '提交的信息不能为空', 'success': False, 'code': 501})  # 提交数据不全
        return JsonResponse(resp_data)

    card = UserBankCard.objects.filter(user_id=user_id, card_no=card_no)
    card.is_delete = True
    card.save()
    resp_data.update({'message': '删除成功'})
    del resp_data['data']
    return JsonResponse(resp_data)


@check_login
@require_GET
def get_balance(request):
    # 获取所有银行卡
    user_id = request.session.get('user_id')
    resp_data = API_RESPONSE_FORMAT.copy()

    user = BankUser.objects.get(id=user_id)
    resp_data.update({'message': '', 'data': {
        'balance': float(user.money),
        'name': user.name
    }})

    return JsonResponse(resp_data)
