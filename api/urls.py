#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/25  0025

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^server.html$', views.server),
]
