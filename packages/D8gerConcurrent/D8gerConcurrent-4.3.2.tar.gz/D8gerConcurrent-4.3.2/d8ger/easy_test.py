#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import os
import ssl
from decimal import *
from concurrent.futures.thread import ThreadPoolExecutor

import numpy as np
import requests

# 屏蔽HTTPS证书校验, 忽略安全警告
requests.packages.urllib3.disable_warnings()
context = ssl._create_unverified_context()
body_file_name = os.path.expanduser('~') + "/d8gerConcurrent.json"
url = ""
method = "GET"
request_headers = {}
request_body= {}
# D8GER just for joke


def init_param() -> list:
    """
    初始化参数, 读取shell命令参数, 自动登录
    依次返回httpie_view方式, 线程池, 登录cookie
    :rtype: list
    """
    parser = argparse.ArgumentParser(description="并发执行接口")
    parser.add_argument("-f", "--filepath", type=str, help="Body数据文件")
    parser.add_argument("-u", "--url", type=str, help="接口请求地址")
    parser.add_argument("-w", "--workers", type=int, choices=choice_nums(1, 65, 1), default=1, help="并发执行线程数, 取值范围[1, 64]")
    parser.add_argument("-l", "--loops", type=int, default=1, help="循环执行次数")
    args = parser.parse_args()
    loops = args.loops
    if loops < 1:
        loops = 1
    global body_file_name
    if (args.filepath is not None) and (not str.isspace(args.filepath)):
        body_file_name = args.filepath
    global url
    url = args.url
    print("============================================================================")
    print("并发参数设置结果: \n\t执行次数=[{}]\n\t并发线程数=[{}]".format(loops, args.workers))
    init_executor = ThreadPoolExecutor(max_workers=args.workers)
    return [loops, init_executor, url]


def choice_nums(start: int, end: int, delta: int) -> list:
    """
    返回指定的数组序列
    :rtype: list
    """
    return np.arange(start, end, delta).tolist()


def parseRequest():
    global body_file_name
    global url
    global method
    global request_headers
    global request_body
    global isJson
    if (body_file_name is not None) and (not str.isspace(body_file_name)):
        try:
            with open(body_file_name, 'r') as request_data:
                request_json = json.load(request_data)
                if url is None or str.isspace(url):
                    url = request_json['url']
                method = request_json['method']
                request_headers = handle_json_str_value(request_json['headers'])
                if request_headers['Content-Type'] == 'application/json':
                    isJson = True
                else:
                    isJson = False
                request_body = request_json['body']
        except Exception as e:
            print("不存在{}文件, 请先创建并按照JSON格式填写请求数据".format(body_file_name))
            print("示例body.json:")
            default_post = {
                "url": "https://xxx.bytedance.com/d8ger/queryMoney",
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json",
                    "x-mock-user": "3103165",
                    "mToken": "XXXXXXXX",
                    "Cookie": "XXXXXXX"
                },
                "body": {
                    "A": "1",
                    "B": "2",
                    "C": 0,
                    "D": "4"
                }
            }
            print(json.dumps(default_post, ensure_ascii=False, indent=4))
            exit(0)
    print("HTTP请求参数: \n\t请求url=[{}]\n\t请求方式=[{}]\n\t请求Headers=[{}]\n\t请求Body数据=[{}]\n".format(
            url,
            method,
            json.dumps(request_headers),
            request_body
        )
    )
    print("============================================================================")


def execute_http(i):
    """
    执行excuteUrl.json接口
    :param i 仅用于计数虚拟参数
    :return:
    """
    response_text = "无响应文本"
    execute_start_time = datetime.datetime.now()
    try:
        if isJson:
            response = requests.request(method, url, headers=request_headers, json=request_body, timeout=60, verify=False)
            # JSON标准格式
            response_text = response.text
        else:
            response = requests.request(method, url, headers=request_headers, data=request_body.encode(), timeout=60, verify=False)
            response_text = response.text
    except Exception as e:
        print(e)
    execute_end_time = datetime.datetime.now()
    delta_microsecond_time = (execute_end_time.timestamp() - execute_start_time.timestamp()) * 1000
    cost_time = Decimal(delta_microsecond_time).quantize(Decimal('0.00'))
    print("#############第[{}]次请求#############\n\texecute_start_time=[{}], execute_end_time=[{}], 耗时=[{}ms]\n\t响应结果:{}\n".format(
        i+1,
        execute_start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        execute_end_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
        cost_time,
        response_text)
    )
    return cost_time


def handle_json_str_value(json):
    """
    将json的值都变为字符串处理
    :param json:
    :return:
    """
    for (k, v) in json.items():
        json[k] = str(v)
    return json


def main():
    # 全局变量
    global execute_num
    global executor
    # 初始化参数
    initial_param_list = init_param()
    execute_num = initial_param_list[0]
    executor = initial_param_list[1]
    nums = list(range(0, execute_num))
    parseRequest()
    times = []
    for result in executor.map(execute_http, nums):
        times.append(result)
    print("============================================================================")
    average_cost_time = np.mean(times)
    median_cost_time = np.median(times)
    print(*times, sep=',')
    print("平均耗时=[{}ms], 中位耗时=[{}ms]".format(Decimal(average_cost_time).quantize(Decimal('0.00')), Decimal(median_cost_time).quantize(Decimal('0.00'))))
    print("============================================================================")
