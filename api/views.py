from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
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
    return HttpResponse("已收到")

