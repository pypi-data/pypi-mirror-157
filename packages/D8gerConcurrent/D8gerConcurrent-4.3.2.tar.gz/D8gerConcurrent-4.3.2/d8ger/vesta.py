#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import requests
import argparse
import os
import json
import ssl

# 屏蔽HTTPS证书校验, 忽略安全警告
requests.packages.urllib3.disable_warnings()
context = ssl._create_unverified_context()


def init_parse_gc_file() -> list:
    """
    初始化参数, 读取shell命令参数
    依次返回: GC日志文件全路径
    :rtype: str
    """
    parser = argparse.ArgumentParser(description="GC日志文件参数解析器")
    parser.add_argument("-f", "--filepath", type=str, help="GC日志文件全路径, 示例 ~/Desktop/gc.log.0.current")
    parser.add_argument("-n", "--name", type=str, help="GC日志文件重命名, 示例 gc.MAPI.log")
    args = parser.parse_args()
    gc_file = args.filepath
    if gc_file is None or len(gc_file) == 0 or str.isspace(gc_file):
        print("请指定目标GC日志文件全路径, 示例 ~/Desktop/gc.log.0.current")
        exit(0)
    split = os.path.split(gc_file)
    gc_rename = args.name
    if gc_rename is None or len(gc_rename) == 0 or str.isspace(gc_rename):
        gc_rename = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + "_" + split[1]
    print("目标GC日志文件: {}\n上传文件名称{}".format(gc_file, gc_rename))
    return [gc_file, gc_rename]


def send_file_to_server(filepath, target_file_name):
    size_m = os.path.getsize(filepath) / float(1024 * 1024)
    print("目标GC文件size: {}MB".format(round(size_m, 2)))
    content = ''
    with open(filepath, 'r') as f:
        content = f.read()
    request_body = {
        'filename': target_file_name,
        'content': content,
    }

    try:
        response = requests.request("POST", "http://gclog.byted.org/upload", json=request_body, timeout=15, verify=False)
        # JSON标准格式
        response_body = json.dumps(response.json(), ensure_ascii=False, indent=4)
        print("\nvesta平台响应:\n{}\n".format(response_body))
    except Exception as err:
        print(str(err))

    print("VestaPlatform地址: http://vesta.byted.org/tool_gcv\nGC文件分析地址: http://gclog.byted.org/download/" + target_file_name)


def main():
    gc_file_params = init_parse_gc_file()
    send_file_to_server(gc_file_params[0], gc_file_params[1])


if __name__ == '__main__':
    main()
