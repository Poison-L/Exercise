#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

"""
通过反射拿相关信息
"""

from django.conf import settings
from repository import models
import importlib
from .server import Server


class PluginManager(object):
    def __init__(self):
        self.plugin_items = settings.PLUGIN_ITEMS
        self.basic_key = "basic"
        self.board_key = "board"

    def exec(self, server_dict):
        # 默认为1 ---> 1,执行完全成功； 2, 局部失败；3，执行失败;4. 服务器不存在
        ret = {'status_code': 1, 'msg': None}
        hostname = server_dict[self.basic_key]['data']['hostname']
        # 通过hostname主机名获取server对象
        server_obj = models.Server.objects.filter(hostname=hostname).first()
        if not server_obj:
            ret['status_code'] = 4
            return ret

        # 实例化Server对象并传参server_obj, server_dict['basic']，server_dict['board']
        obj = Server(server_obj, server_dict[self.basic_key], server_dict[self.board_key])
        # plugins/server.py
        obj.process()
        # 对比更新[硬盘，网卡，内存，可插拔的插件]
        for k, v in self.plugin_items.items():
            try:
                # api.plugins.disk.Disk
                module_path, cls_name = v.rsplit('.', maxsplit=1)
                # 导入module_path模块 api.plugins.disk
                md = importlib.import_module(module_path)
                # 模块内找到相应的类
                cls = getattr(md, cls_name)
                # 实例化类对象并传参server_obj,server_dict['disk']...
                obj = cls(server_obj, server_dict[k])
                # plugins/disk.py,nic.py,memory.py
                obj.process()
            except Exception as e:
                ret['status_code'] = 2
        # ret状态信息字典返回views 再由视图返回客户端
        return ret





