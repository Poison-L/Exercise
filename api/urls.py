#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/25  0025

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^server.html$', views.server),
    # API验证
    url(r'^test.html$', views.test),
    # 事务
    url(r'^tran.html$', views.tran),
]
