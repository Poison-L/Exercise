#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

from repository import models
import datetime


class Server(object):
    def __init__(self, server_obj, basic_dict, board_dict):
        self.server_obj = server_obj
        self.basic_dict = basic_dict    # server_dict['basic']
        self.board_dict = board_dict    # server_dict['board']

    def process(self, ):
        # server对象存在 新老数据对比 更新Server表
        temp = {}
        temp.update(self.basic_dict['data'])
        temp.update(self.board_dict['data'])
        # 旧数据server_obj.sn  新数据temp['sn']
        # if server_obj.sn != temp['sn']:
        #     record = "[%s]的[%s]由[%s]变更为[%s]" % (hostname, 'sn', server_obj.sn, temp['sn'])
        #     server_obj.sn = temp['sn']
        # server_obj.save()

        # 新老数据对比 服务器数据更新
        temp.pop('hostname')
        server_record_list = []
        for k, new_val in temp.items():
            # 通过反射取看k字段对应的数据库旧值
            old_val = getattr(self.server_obj, k)
            if old_val != new_val:
                server_record = "[%s]的[%s]由[%s]变更为[%s]" % (self.server_obj.hostname, k, old_val, new_val)
                server_record_list.append(server_record)
                setattr(self.server_obj, k, new_val)
        self.server_obj.save()
        if server_record_list:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(server_record_list))


