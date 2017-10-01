#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

from repository import models


class Disk(object):
    def __init__(self, server_obj, info):
        self.server_obj = server_obj
        self.disk_dict = info

    def process(self):
        pass
