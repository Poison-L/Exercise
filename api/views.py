from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from repository import models
import json
from .plugins import PluginManager
# Create your views here.


# 引入模块 装饰器去除csrf_token认证
@ csrf_exempt
def server(request):
    # 打印接收到的client端数据
    # print(request.POST)
    # print(request.body)
    # 客户端提交的最新资产数据 字节decode字符串 再loads成字典
    server_dict = json.loads(request.body.decode("utf-8"))
    # print(type(server_dict), server_dict)
    # 检查server表中是否有当前资产信息【主机名是唯一标识】
    if not server_dict['basic']['status']:
        return HttpResponse("无法获取")
    hostname = server_dict['basic']['data']['hostname']
    # 通过hostname主机名获取server对象
    server_obj = models.Server.objects.filter(hostname=hostname).first()
    if not server_obj:
        # 创建服务器信息 实际不可创建
        temp = {}
        temp.update(server_dict['basic']['data'])
        temp.update(server_dict['board']['data'])
        server_obj = models.Server.objects.create(**temp)

        # 创建硬盘信息
        """
        缺少：需判断信息是否获取成功，如果未获取成功需要放到错误日志表
        """
        disk_info_dict = server_dict['disk']['data']
        # dict.values()以列表返回字典中的所有值
        for item in disk_info_dict.values():
            # 绑定FK关系 即外键增加字段
            # item['server_obj_id'] = server_obj.id
            item['server_obj'] = server_obj
            models.Disk.objects.create(**item)

        # 创建内存信息
        memory_info_dict = server_dict['memory']['data']
        for item in memory_info_dict.values():
            item['server_obj'] = server_obj
            models.Memory.objects.create(**item)

        # 创建网卡信息
        nic_info_dict = server_dict['nic']['data']
        # dict.items() 以列表返回可遍历的(键, 值) 元组数组
        for k, v in nic_info_dict.items():
            v['server_obj'] = server_obj
            v['name'] = k
            models.NIC.objects.create(**v)

        return HttpResponse("已收到")

    else:
        # server对象存在 新老数据对比 更新Server表
        temp = {}
        temp.update(server_dict['basic']['data'])
        temp.update(server_dict['board']['data'])
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
            old_val = getattr(server_obj, k)
            if old_val != new_val:
                server_record = "[%s]的[%s]由[%s]变更为[%s]" % (hostname, k, old_val, new_val)
                server_record_list.append(server_record)
                setattr(server_obj, k, new_val)
        server_obj.save()
        if server_record_list:
            models.ServerRecord.objects.create(server_obj=server_obj, content='\n'.join(server_record_list))

        """
        缺少：status=False,写错误日志
        """
        new_disk_info_dict = server_dict['disk']['data']
        # 旧硬盘数据对象列表  [obj1,obj2...]
        old_disk_info_list = server_obj.disk.all()
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
            """
            {'slot': '5', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAFB00549A     Samsung SSD 840 PRO Series              DXM06B0Q'}
            {'slot': '2', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1SZNSAFA01085L     Samsung SSD 850 PRO 512GB               EXM01B6Q'}
            """
            value = new_disk_info_dict[slot]
            add_disk = "[%s]添加硬盘:槽位[%s]，类型[%s]，容量[%s]，型号[%s]" % (
                hostname, slot, value['pd_type'], value['capacity'], value['model']
            )
            add_disk_record.append(add_disk)
            value['server_obj'] = server_obj
            models.Disk.objects.create(**value)
        # 创建服务器变更记录
        if add_disk_record:
            models.ServerRecord.objects.create(server_obj=server_obj, content='\n'.join(add_disk_record))

        # 删除硬盘
        del_disk_record = []
        models.Disk.objects.filter(server_obj=server_obj, slot__in=del_slot_list).delete()
        for slot in del_slot_list:
            value = new_disk_info_dict[slot]
            del_disk = "[%s]删除硬盘:槽位[%s]，类型[%s]，容量[%s]，型号[%s]" % (
                hostname, slot, value['pd_type'], value['capacity'], value['model']
            )
            del_disk_record.append(del_disk)
        if del_disk_record:
            models.ServerRecord.objects.create(server_obj=server_obj, content='\n'.join(del_disk_record))

        # 更新硬盘
        update_disk_record = []
        for slot in update_slot_list:
            # 获取更新硬盘信息字典
            value = new_disk_info_dict[slot]
            # 获取数据库槽位对应对象  即旧值
            disk_obj = models.Disk.objects.filter(server_obj=server_obj, slot=slot).first()
            for k, new_val in value.items():
                old_val = getattr(disk_obj, k)
                if old_val != new_val:
                    update_disk = "[%s]更新硬盘[%s]由[%s]变更为[%s]" % (hostname, k, old_val, new_val)
                    update_disk_record.append(update_disk)
                    setattr(disk_obj, k, new_val)
            disk_obj.save()
        if update_disk_record:
            models.ServerRecord.objects.create(server_obj=server_obj, content='\n'.join(update_disk_record))

        return HttpResponse("已收到")


