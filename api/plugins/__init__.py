#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

"""
通过反射拿settings相关
"""

from django.conf import settings
from repository import models


class PluginManager(object):
    def __init__(self):
        self.plugin_items = settings.PLUGIN_ITEMS
        self.basic_key = "basic"
        self.board_key = "board"

    def exec(self, server_dict):
        pass