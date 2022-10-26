# !/usr/bin/env python
# -*- coding: utf-8 -*-


from django.urls import path

from . import manager_view


urlpatterns = [
    path('login/', manager_view.login, name='manager_login'),
    path('register/', manager_view.register, name='manager_register'),
    path('login_handle/', manager_view.login_handle, name='login_handle'),
    path('register_handle/', manager_view.register_handle, name='register_handle'),
    path('index/', manager_view.manager_index, name='manager_index'),

]



