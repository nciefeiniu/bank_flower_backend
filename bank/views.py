from django.shortcuts import render

# Create your views here.

import json

from django.http import HttpResponse, JsonResponse
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from bank.models import BankUser
from bank.default import API_RESPONSE_FORMAT


def get_model_fields(model) -> list:
    fields = [field.name for field in model._meta.get_fields()]
    return fields


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
            resp_data.update({'code': 500, 'message': f'{key} can not be empty!'})
            return JsonResponse(resp_data)
    user = BankUser.create(**body_dict)
    user.save()
    resp_data.update({'message': 'register ok',
                      'data': model_to_dict(user, ['id', 'account', 'name', 'sex', 'money'])})
    return JsonResponse(resp_data)


@require_GET
def check_account_exists(request):
    resp_data = API_RESPONSE_FORMAT.copy()

    account = request.GET.get('account')
    user = BankUser.objects.filter(account=account)
    if user.exists():
        resp_data.update({'message': f'{account} exists!', 'data': {'exists': True}})
        return JsonResponse(resp_data)
    resp_data.update({'message': f'{account} not exists!', 'data': {'exists': False}})
    return JsonResponse(resp_data)


