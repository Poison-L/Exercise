from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from repository import models
import json
# Create your views here.


# 引入模块 装饰器去除csrf_token认证
@ csrf_exempt
def server(request):
    # 打印接受到的client端数据
    # print(request.POST)
    # print(request.body)
    server_dict = json.loads(request.body.decode("utf-8"))
    print(type(server_dict), server_dict)
    # 1. 检查server表中是否有当前资产信息【主机名是唯一标识】
    if not server_dict['basic']['status']:
        return HttpResponse("无法获取")
    hostname = server_dict['basic']['data']['hostname']
    # 通过hostname主机名获取server对象
    server_obj = models.Server.objects.filter(hostname=hostname).first()
    if not server_obj:
        # 没有就创建，服务器和网卡，内存，硬盘...
        pass
    else:
        # 不再创建server对象，新老数据对比
        # 硬盘
        new_disk = server_dict['disk']['data']
        """
        {
            '0': {'slot': '0', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5NV'},
            '1': {'slot': '1', 'pd_type': 'SAS', 'capacity': '279.396', 'model': 'SEAGATE ST300MM0006     LS08S0K2B5AH'},
            '2': {'slot': '2', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1SZNSAFA01085L     Samsung SSD 850 PRO 512GB               EXM01B6Q'},
            '3': {'slot': '3', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAF912433K     Samsung SSD 840 PRO Series              DXM06B0Q'},
            '4': {'slot': '4', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAF303909M     Samsung SSD 840 PRO Series              DXM05B0Q'},
            '5': {'slot': '5', 'pd_type': 'SATA', 'capacity': '476.939', 'model': 'S1AXNSAFB00549A     Samsung SSD 840 PRO Series
        }
        """
        # old_disk = models.Disk.objects.filter(server_obj_id=server_obj.id)
        # old_disk = models.Disk.objects.filter(server_obj=server_obj)
        old_disk = server_obj.disk_set.values("slot", "pd_type", "capacity", "model")
        """
        [
            {'slot': 1, 'model':'xx', 'capacity':'xxx', 'pd_type':'xx'},
            {'slot': 2, 'model':'xx', 'capacity':'xxx', 'pd_type':'xx'},
            {'slot': 3, 'model':'xx', 'capacity':'xxx', 'pd_type':'xx'},
            {'slot': 9, 'model':'xx', 'capacity':'xxx', 'pd_type':'xx'},
        ]
        """
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


