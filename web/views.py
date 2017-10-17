from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from repository import models
import json
import time
from utils.page import Pagination


# Create your views here.


def server(request):
    # 只展示页面框架
    return render(request, 'server.html')


def server_json(request):
    """
    获取数据库数据，通过Ajax方式发送，需转换数据为json格式
    """
    if request.method == "GET":
        # 转换列表嵌套字典 设置为配置且有序 可作为数据返回用户
        search_config = [
            {'name': 'hostname__contains', 'title': '主机名', 'type': 'input'},
            {'name': 'cabinet_num', 'title': "机柜号", 'type': 'input'},
            {'name': 'server_status_id', 'title': '服务器状态', 'type': 'select', 'choice_name': 'status_choices'},
        ]
        # 过滤包含c1的服务器 '__contains'实现模糊查询
        # models.Server.objects.filter(hostname__contains='c1')

        table_config = [
            {
                'q': None,
                'title': '选择',
                'display': True,
                'text': {'tpl': '<input type="checkbox" value="{nid}" />', 'kwargs': {'nid': '@id'}},
                'attr': {'class': 'c1',  'origin': '@id', 'nid': '@id'},
            },
            {
                'q': 'id',
                'title': 'ID',
                # 订制是否显示内容
                'display': False,
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@id'}},
                'attr': {},
            },
            {
                'q': 'hostname',
                'title': '主机名',
                'display': True,
                # 'text': {'tpl': '{a1}-{a2}', 'kwargs': {'a1': '@hostname', 'a2': '666'}},
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@hostname', }},
                'attr': {'class': 'c1', 'edit': 'true', 'origin': '@hostname', 'name': 'hostname'},
            },
            {
                'q': 'sn',
                'title': '序列号',
                'display': True,
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@sn'}},
                'attr': {'class': 'c1', 'edit': 'true', 'origin': '@sn', 'name': 'sn'},
            },
            {
                'q': 'os_platform',
                'title': '系统',
                'display': True,
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@os_platform'}},
                'attr': {'class': 'c1', 'edit': 'true', 'origin': '@os_platform', 'name': 'os_platform'},
            },
            {
                'q': 'os_version',
                'title': '系统版本',
                'display': True,
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@os_version'}},
                'attr': {'class': 'c1', 'origin': '@os_version', 'name': 'os_version'},
            },
            {
                # 跨表查询
                'q': 'business_unit__name',
                'title': '业务线',
                'display': True,
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@business_unit__name'}},
                'attr': {'class': 'c1'},
            },
            {
                'q': 'server_status_id',
                'title': '服务器状态',
                'display': True,
                'text': {'tpl': '{a1}', 'kwargs': {'a1': '@@status_choices'}},
                'attr': {'class': 'c1', 'edit': 'true', 'edit-type': 'select', 'choice-key': 'status_choices',
                         'origin': '@server_status_id', 'name': 'server_status_id'},
            },
            {
                'q': None,
                'title': '操作',
                'display': True,
                'text': {'tpl': '<a href="/edit/{nid}/">编辑</a> | <a href="/del/{uid}/">删除</a> ',
                         'kwargs': {'nid': '@id', 'uid': '@id'}},
                'attr': {},
            },
        ]

        values = []
        for item in table_config:
            # 不为空数据库取值
            if item['q']:
                values.append(item['q'])

        # 获取搜索条件
        condition_dict = json.loads(request.GET.get('condition'))
        """
        {
             server_status_id: [1,2],
             hostname: ['c1.com','c2.com'],
         }
        """
        from django.db.models import Q
        # 构造搜索条件
        con = Q()
        for k, v in condition_dict.items():
            temp = Q()
            temp.connector = 'OR'
            for item in v:
                temp.children.append((k, item,))
            con.add(temp, 'AND')

        # 获取用户请求的页码
        current_page = request.GET.get('pageNum')
        total_item_count = models.Server.objects.filter(con).count()

        page_obj = Pagination(current_page, total_item_count, per_page_count=3)

        # QuerySet嵌套字典 传列表*values 传字典**
        server_list = models.Server.objects.filter(con).values(*values)[page_obj.start:page_obj.end]
        # 创建返回前端数据的response字典
        response = {
            'search_config': search_config,
            'data_list': list(server_list),
            'table_config': table_config,
            'global_choices_dict': {
                # 生成前端中文显示以及下拉框select选项
                'status_choices': models.Server.server_status_choices,
            },
            'page_html': page_obj.page_html_js()
        }
        time.sleep(0.5)

        # return HttpResponse(json.dumps(response))
        # json后为列表
        return JsonResponse(response)

    elif request.method == "DELETE":
        id_list = json.loads(request.body.decode('utf-8'))
        response = {'status': True, 'msg': None}
        try:
            # models.Server.objects.filter(id__in=id_list).delete()
            pass
        except Exception as e:
            response['status'] = False
            response['msg'] = str(e)
        return HttpResponse(json.dumps(response))

    elif request.method == "PUT":
        update_list = json.loads(request.body.decode('utf-8'))

        response = {'status': True, 'msg': None}
        try:
            for row in update_list:
                nid = row.pop('nid')
                # models.Server.objects.filter(id=nid).update(**row)
            print(update_list)
        except Exception as e:
            response['status'] = False
            response['msg'] = str(e)
        return HttpResponse(json.dumps(response))


def disk(request):
    return render(request, 'disk.html')


def disk_json(request):

    # 转换列表嵌套字典 设置为配置 可作为数据返回用户
    table_config = [
        {
            'q': None,
            'title': '选择',
            'display': True,
            'text': {'tpl': '<input type="checkbox" value="{nid}" />', 'kwargs': {'nid': '@id'}},
        },
        {
            'q': 'id',
            'title': 'ID',
            'display': False,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@id'}},
        },
        {
            'q': 'slot',
            'title': '硬盘槽位',
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@slot'}},
        },
        {
            'q': 'model',
            'title': '硬盘型号',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@model'}},
        },
        {
            'q': 'capacity',
            'title': '硬盘容量（GB）',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@capacity'}},
        },
        {
            'q': 'pd_type',
            'title': '硬盘类型',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@pd_type'}},
        },
        {
            # 跨表查询
            'q': 'server_obj__hostname',
            'title': '所属服务器',
            'display': True,
            'text': {'tpl': '{a1}', 'kwargs': {'a1': '@server_obj__hostname'}},
        },
        {
            'q': None,
            'title': '操作',
            'display': True,
            'text': {'tpl': '<a href="/edit/{nid}/">编辑</a> | <a href="/del/{uid}/">删除</a> ',
                     'kwargs': {'nid': '@id', 'uid': '@id'}},
        },
    ]

    values = []
    for item in table_config:
        if item['q']:
            values.append(item['q'])
    # QuerySet嵌套字典 传列表*values 传字典**
    disk_list = models.Disk.objects.values(*values)
    # 创建返回前端数据的response字典
    response = {
        'data_list': list(disk_list),
        'table_config': table_config
    }
    time.sleep(0.5)

    # return HttpResponse(json.dumps(response))
    return JsonResponse(response)


# ====================== 模板语言显示choice ====================== #

# def test(request):
#     """
#
#     get_xxx_display() 对象方法
#     """
#     server_list = models.Server.objects.all()
#     for row in server_list:
#        print(row.id,row.hostname,row.business_unit.name,"===",row.server_status_id,row.get_server_status_id_display())


def test(request):
    """
    模板语言显示choice
    """
    def xxx(server_list):
        # data_list，QuerySet集合[{},{}]  xxx函数可单独拿到test函数外 与在内部效果等同
        for row in server_list:
            # 前端触发后执行，一次循环
            for item in models.Server.server_status_choices:
                # item[0] 1,2,3,4
                if item[0] == row['server_status_id']:
                    # 字典row添加server_status_id_name键值对
                    row['server_status_id_name'] = item[1]
                    break
            # 生成器
            yield row

    data_list = models.Server.objects.all().values('hostname', 'server_status_id')
    # xxx(data_list) 将功能通过生成器的方式返回前端模板语言
    return render(request, 'test.html', {'server_list': xxx(data_list)})
