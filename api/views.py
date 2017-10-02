
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from repository import models
import json
from .plugins import PluginManager
from datetime import date
from django.db.models import Q
import time
# Create your views here.


# 引入模块 装饰器去除csrf_token认证
@ csrf_exempt
def server(request):
    # GET请求返回当前未采集数据
    if request.method =="GET":
        # 获取年月日
        current_date = date.today()
        # 获取今日未采集的主机列表
        host_list = models.Server.objects.filter(
            # None首次录入 latest_date__date最后更改时间只取年月日 server_status_id=2 服务器在线状态
            Q(Q(latest_date=None) | Q(latest_date__date__lt=current_date)) & Q(server_status_id=2)
        ).values('hostname')
        host_list = list(host_list)
        # 转换为列表进行json操作
        return HttpResponse(json.dumps(host_list))

    elif request.method =="POST":
        # 打印接收到的client端数据
        # print(request.POST)
        # print(request.body)
        # 客户端提交的最新资产数据 字节decode字符串 再loads成字典
        server_dict = json.loads(request.body.decode("utf-8"))
        # print(type(server_dict), server_dict)
        # 检查server表中是否有当前资产信息【主机名是唯一标识】
        if not server_dict['basic']['status']:
            return HttpResponse("无法获取")
        # 实例化PluginManager对象
        manager = PluginManager()
        # 获取response字典  执行plugins/__init__/PluginManager exec方法 并传参server_dict
        response = manager.exec(server_dict)
        # 将状态信息返回客户端
        return HttpResponse(json.dumps(response))

