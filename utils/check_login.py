# !/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import redirect


def check_login(fn):
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_login', 'false') == 'true':
            return fn(request, *args, *kwargs)
        else:
            response = HttpResponse('')
            response.status_code = 555  # 555 需要登录
            return response

    return wrapper


def check_login_redirect(redirect_url=None):
    def check(fn):
        def wrapper(request, *args, **kwargs):
            if request.session.get('is_login', 'false') == 'true':
                return fn(request, *args, *kwargs)
            else:
                if redirect_url:
                    return redirect(redirect_url)
                response = HttpResponse('')
                response.status_code = 555  # 555 需要登录
                return response

        return wrapper

    return check
