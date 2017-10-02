#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Robert"
# Date: 2017/9/30  0030

from repository import models


class Memory(object):
    def __init__(self, server_obj, info):
        self.server_obj = server_obj
        self.memory_dict = info    # server_dict['memory']

    def process(self):
        # 采集新数据字典
        new_memory_info_dict = self.memory_dict['data']
        # 旧内存数据对象列表  [obj1,obj2...]
        old_memory_info_list = self.server_obj.memory.all()
        # 获取新内存数据槽位  dict.keys()以列表返回一个字典所有的键
        new_memory_slot_set = set(new_memory_info_dict.keys())
        old_memory_slot_set = {obj.slot for obj in old_memory_info_list}
        # c = t – s  求差集（项在t中，但不在s中）
        add_slot_list = new_memory_slot_set.difference(old_memory_slot_set)
        del_slot_list = old_memory_slot_set.difference(new_memory_slot_set)
        # 交集
        update_slot_list = new_memory_slot_set.intersection(old_memory_slot_set)

        # 增加内存
        add_memory_record = []
        # 获取添加槽位
        for slot in add_slot_list:
            # 获取添加内存信息字典
            value = new_memory_info_dict[slot]
            """
            {'capacity': 1024, 'slot': 'DIMM #0', 'model': 'DRAM', 'speed': '667 MHz', 'manufacturer': 'Not Specified', 'sn': 'Not Specified'}
            {'capacity': 0, 'slot': 'DIMM #2', 'model': 'DRAM', 'speed': '667 MHz', 'manufacturer': 'Not Specified', 'sn': 'Not Specified'}                    
            """
            add_memory = "[%s]添加内存:容量[%s]，槽位[%s]，型号[%s]，速度[%s]，制造商[%s]，SN号[%s]" % (
                self.server_obj.hostname, value['capacity'], slot, value['model'], value['speed'],
                value['manufacturer'], value['sn']
            )
            add_memory_record.append(add_memory)
            value['server_obj'] = self.server_obj
            models.Memory.objects.create(**value)
        # 创建服务器变更记录
        if add_memory_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(add_memory_record))

        # 删除内存
        del_memory_record = []
        for slot in del_slot_list:
            dict = models.Memory.objects.filter(slot=slot).values(
                'capacity', 'model', 'speed', 'manufacturer', 'sn').first()
            del_memory = "[%s]删除内存:容量[%s]，槽位[%s]，型号[%s]，速度[%s]，制造商[%s]，SN号[%s]" % (
                self.server_obj.hostname, dict['capacity'], slot, dict['model'], dict['speed'],
                dict['manufacturer'], dict['sn']
            )
            del_memory_record.append(del_memory)
        models.Memory.objects.filter(server_obj=self.server_obj, slot__in=del_slot_list).delete()
        if del_memory_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(del_memory_record))

        # 更新内存
        update_memory_record = []
        for slot in update_slot_list:
            # 获取更新内存信息字典
            value = new_memory_info_dict[slot]
            # 获取数据库槽位对应对象  即旧值
            memory_obj = models.Memory.objects.filter(server_obj=self.server_obj, slot=slot).first()
            for k, new_val in value.items():
                old_val = getattr(memory_obj, k)
                if old_val != new_val:
                    update_memory = "[%s]更新内存:槽位[%s]，[%s]由[%s]变更为[%s]" % (
                        self.server_obj.hostname, slot, k, old_val, new_val
                    )
                    update_memory_record.append(update_memory)
                    setattr(memory_obj, k, new_val)
            memory_obj.save()
        if update_memory_record:
            models.ServerRecord.objects.create(server_obj=self.server_obj, content='\n'.join(update_memory_record))
