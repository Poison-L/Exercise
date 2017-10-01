#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

from repository import models
import datetime


class Server(object):
    def __init__(self, server_obj, basic_dict, board_dict):
        self.server_obj = server_obj
        self.basic_dict = basic_dict
        self.board_dict = board_dict

    def process(self, ):
        pass
