from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from repository import models
import json
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
        # 创建服务器信息
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

        temp.pop('hostname')
        record_list = []
        for k, new_val in temp.items():
            # 通过反射取看k字段对应的数据库旧值
            old_val = getattr(server_obj, k)
            if old_val != new_val:
                record = "[%s]的[%s]由[%s]变更为[%s]" % (hostname, k, old_val, new_val)
                record_list.append(record)
                setattr(server_obj, k, new_val)
        server_obj.save()
        if record_list:
            models.ServerRecord.objects.create(server_obj=server_obj, content=';'.join(record_list))

        # 硬盘
        # new_disk = server_dict['disk']['data']



        # old_disk = models.Disk.objects.filter(server_obj_id=server_obj.id)
        # old_disk = models.Disk.objects.filter(server_obj=server_obj)
        # old_disk = server_obj.disk_set.values("slot", "pd_type", "capacity", "model")



        # set集合
        # 根据槽位进行比较： new_disk有，old_disk没有 ->  0,4,5   create(**dic)
        # 根据槽位进行比较： old_disk有，new_disk没有 ->  0,4,5   delete

        # 根据槽位进行比较： old_disk有，new_disk有 ->  1,2,3     update

        # 需求：
        #      更新时，记录： xx服务器，槽位，xxx由于xx变更为xx
        # 修改：update
        # obj = modelx..xxxx.first()
        # obj.model = "xxxx"
        # obj. pdtype = "xxx"
        # obj.save()

        return HttpResponse("已收到")


