
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from repository import models
import json
from .plugins import PluginManager
from datetime import date
from django.db.models import Q
import time
import hashlib
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
        ).values('hostname')[0:200]
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


# ======================================  API验证示例 ====================================== #
def md5(arg):
    hs = hashlib.md5()
    hs.update(arg.encode('utf-8'))
    return hs.hexdigest()


key = "fekjsbfhefousdnjdksfbp"
# 一般放在内存或缓存内 设置超时时间自动清除
visited_keys = {
    # "8d75d09db9c6fbfa508c87d3b60926f5": 时间戳
}


def api_auth(func):
    """
    API验证（*），Tornado签名cookie源码
    """
    def inner(request, *args, **kwargs):
        # 获取服务端时间戳
        server_float_ctime = time.time()
        # 通过META字典取看key
        auth_header_val = request.META.get('HTTP_AUTH_API')
        # 取client端 md5_str和时间戳  8d75d09db9c6fbfa508c87d3b60926f5|1507029355.926232
        client_md5_str, client_ctime = auth_header_val.split('|', maxsplit=1)
        client_float_ctime = float(client_ctime)

        # 第一关 有效时间10秒验证
        if (client_float_ctime + 10) < server_float_ctime:
            return HttpResponse('别低头，王冠会掉！')

        # 第二关 MD5时间戳加密验证
        server_md5_str = md5("%s|%s" % (key, client_ctime))
        if server_md5_str != client_md5_str:
            return HttpResponse('你有毒吧...')

        # 第三关 验证visited_keys是否已经存在值
        if visited_keys.get(client_md5_str):
            return HttpResponse('What are you 弄啥嘞！')

        visited_keys[client_md5_str] = client_float_ctime
        return func(request, *args, **kwargs)

    return inner


@api_auth
def test(request):
    return HttpResponse("原来是自己人啊...")

