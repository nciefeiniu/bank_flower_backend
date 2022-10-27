# !/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register_account, name='register'),
    path('check_account_exists/', views.check_account_exists, name='check_account_exists'),
    path('login/', views.login, name='login'),
    path('recharge/', views.recharge, name='recharge'),
    path('with_drawal/', views.with_drawal, name='with_drawal'),
    path('transfer_accounts/', views.transfer_accounts, name='transfer_accounts'),
    path('add_card/', views.add_card, name='add_card'),
    path('recharge_phone_bill/', views.recharge_phone_bill, name='recharge_phone_bill'),
    path('buy_stock/', views.buy_stock, name='buy_stock'),
    path('get_all_card/', views.get_all_card, name='get_all_card'),
    path('get_balance/', views.get_balance, name='get_balance'),
    path('get_all_record/', views.get_all_record, name='get_all_record'),
    path('del_card/', views.del_card, name='del_card'),
    path('get_all_stock_record/', views.get_all_stock_record, name='get_all_stock_record'),

]