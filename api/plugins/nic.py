#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

from repository import models


class Nic(object):
    def __init__(self, server_obj, info):
        self.server_obj = server_obj
        self.nic_dict = info    # server_dict['nic']

    def process(self):
        # 采集新数据字典
        new_nic_info_dict = self.nic_dict['data']
        # 旧网卡数据对象列表  [obj1,obj2...]
        old_nic_info_list = self.server_obj.nic.all()
        # 获取新网卡数据名称  dict.keys()以列表返回一个字典所有的键
        new_nic_name_set = set(new_nic_info_dict.keys())
        old_nic_name_set = {obj.name for obj in old_nic_info_list}
        # c = t – s  求差集（项在t中，但不在s中）
        add_name_list = new_nic_name_set.difference(old_nic_name_set)
        del_name_list = old_nic_name_set.difference(new_nic_name_set)
        # 交集
        update_name_list = new_nic_name_set.intersection(old_nic_name_set)

        # 增加网卡
        add_nic_record = []
        # 获取添加名称
        for name in add_name_list:
            # 获取添加网卡信息字典
            value = new_nic_info_dict[name]
            """
            {'up': True, 'hwaddr': '00:1c:42:a5:57:7a', 'ipaddrs': '10.211.55.4', 'netmask': '255.255.255.0'}
            """
            add_nic = "[%s]添加网卡:名称[%s]，状态[%s]，mac地址[%s]，ip地址[%s]，netmask[%s]" % (
                self.server_obj.hostname, name, value['up'], value['hwaddr'], value['ipaddrs'], value['netmask']
            )
            add_nic_record.append(add_nic)
            value['name'] = name
            value['server_obj'] = self.server_obj
            models.NIC.objects.create(**value)
        # 创建服务器变更记录
        if add_nic_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(add_nic_record))

        # 删除网卡
        del_nic_record = []
        for name in del_name_list:
            dict = models.NIC.objects.filter(name=name).values('up', 'hwaddr', 'ipaddrs', 'netmask').first()
            del_nic = "[%s]删除网卡:名称[%s]，状态[%s]，mac地址[%s]，ip地址[%s]，netmask[%s]" % (
                self.server_obj.hostname, name, dict['up'], dict['hwaddr'], dict['ipaddrs'], dict['netmask']
            )
            del_nic_record.append(del_nic)
        models.NIC.objects.filter(server_obj=self.server_obj, name__in=del_name_list).delete()
        if del_nic_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(del_nic_record))

        # 更新网卡
        update_nic_record = []
        for name in update_name_list:
            # 获取更新网卡信息字典
            value = new_nic_info_dict[name]
            # 获取数据库名称对应对象  即旧值
            nic_obj = models.NIC.objects.filter(server_obj=self.server_obj, name=name).first()
            for k, new_val in value.items():
                old_val = getattr(nic_obj, k)
                if old_val != new_val:
                    update_nic = "[%s]更新网卡:名称[%s]，[%s]由[%s]变更为[%s]" % (
                        self.server_obj.hostname, name, k, old_val, new_val
                    )
                    update_nic_record.append(update_nic)
                    setattr(nic_obj, k, new_val)
            nic_obj.save()
        if update_nic_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(update_nic_record))

