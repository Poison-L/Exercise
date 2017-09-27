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
        pass
    else:
        new_disk = server_dict['disk']['data']
        old_disk = server_obj.disk_set.values("slot", "pd_type", "capacity", "model")

        return HttpResponse("已收到")


