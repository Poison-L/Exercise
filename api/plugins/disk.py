#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

from repository import models


class Disk(object):
    def __init__(self, server_obj, info):
        self.server_obj = server_obj
        self.disk_dict = info   # server_dict['disk']

    def process(self):
        """
        缺少：status=False,写错误日志
        """
        # 采集新数据字典
        new_disk_info_dict = self.disk_dict['data']
        # 旧硬盘数据对象列表  [obj1,obj2...]
        old_disk_info_list = self.server_obj.disk.all()
        # 获取新硬盘数据槽位  dict.keys()以列表返回一个字典所有的键
        new_disk_slot_set = set(new_disk_info_dict.keys())
        old_disk_slot_set = {obj.slot for obj in old_disk_info_list}
        # c = t – s  求差集（项在t中，但不在s中）
        add_slot_list = new_disk_slot_set.difference(old_disk_slot_set)
        del_slot_list = old_disk_slot_set.difference(new_disk_slot_set)
        # 交集
        update_slot_list = new_disk_slot_set.intersection(old_disk_slot_set)

        # 增加硬盘
        add_disk_record = []
        # 获取添加槽位
        for slot in add_slot_list:
            # 获取添加硬盘信息字典
            value = new_disk_info_dict[slot]
            """
            {'slot': '5', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAFB00549A     Samsung SSD 840 PRO Series              DXM06B0Q'}
            {'slot': '2', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1SZNSAFA01085L     Samsung SSD 850 PRO 512GB               EXM01B6Q'}
            """
            add_disk = "[%s]添加硬盘:槽位[%s]，类型[%s]，容量[%s]，型号[%s]" % (
                self.server_obj.hostname, slot, value['pd_type'], value['capacity'], value['model']
            )
            add_disk_record.append(add_disk)
            value['server_obj'] = self.server_obj
            models.Disk.objects.create(**value)
        # 创建服务器变更记录
        if add_disk_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(add_disk_record))

        # 删除硬盘
        del_disk_record = []
        for slot in del_slot_list:
            dict = models.Disk.objects.filter(slot=slot).values('pd_type', 'capacity', 'model').first()
            del_disk = "[%s]删除硬盘:槽位[%s]，类型[%s]，容量[%s]，型号[%s]" % (
                self.server_obj.hostname, slot, dict['pd_type'], dict['capacity'], dict['model']
            )
            del_disk_record.append(del_disk)
        models.Disk.objects.filter(server_obj=self.server_obj, slot__in=del_slot_list).delete()
        if del_disk_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(del_disk_record))

        # 更新硬盘
        update_disk_record = []
        for slot in update_slot_list:
            # 获取更新硬盘信息字典
            value = new_disk_info_dict[slot]
            # 获取数据库槽位对应对象  即旧值
            disk_obj = models.Disk.objects.filter(server_obj=self.server_obj, slot=slot).first()
            for k, new_val in value.items():
                old_val = getattr(disk_obj, k)
                if old_val != new_val:
                    update_disk = "[%s]更新硬盘:槽位[%s]，[%s]由[%s]变更为[%s]" % (
                        self.server_obj.hostname, slot, k, old_val, new_val
                    )
                    update_disk_record.append(update_disk)
                    setattr(disk_obj, k, new_val)
            disk_obj.save()
        if update_disk_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(update_disk_record))
