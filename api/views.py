from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
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
    # 实例化PluginManager对象
    manager = PluginManager()
    # 获取response字典  执行plugins/__init__/PluginManager exec方法 并传参server_dict
    response = manager.exec(server_dict)
    # 将状态信息返回客户端
    return HttpResponse(json.dumps(response))

