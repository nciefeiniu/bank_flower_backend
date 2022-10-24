# !/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register_account, name='register'),
    path('check_account_exists/', views.check_account_exists, name='check_account_exists'),
]