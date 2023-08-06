#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import ssl
import os

import requests

# 屏蔽HTTPS证书校验, 忽略安全警告
requests.packages.urllib3.disable_warnings()
context = ssl._create_unverified_context()


def init_parse_app_config() -> list:
    """
    初始化参数, 读取shell命令参数
    依次返回: appId
    :rtype: str
    """
    parser = argparse.ArgumentParser(description="AppId参数解析器")
    parser.add_argument('--nargs', nargs='+', required=True, help="AppId, 示例 9988 7766 5544 ")
    args = parser.parse_args()
    app_id_list = args.nargs
    if app_id_list is None or len(app_id_list) == 0:
        print("请指明AppId, 示例 9988 7766 5544 ")
        exit(0)
    print("目标AppId列表: {}".format(",".join(app_id_list)))
    return app_id_list


def query_app(app_id, env):
    print("{}查询[{}]环境信息...".format(app_id, env))
    request_body = {
        'appId': app_id
    }
    request_header = {
        "Content-Type": "application/json",
        "mToken": "77A98DB54A99429C9D06562AEC34C52D",
        "get-svc": "1"
    }
    domain = ""
    if env == 'BOE':
        domain = "http://mapi-platform-boe.bytedance.net"
    elif env == 'PRE':
        domain = "http://mapi-platform-pre.bytedance.net"
    elif env == "PRD":
        domain = "https://mapi-platform-prd.bytedance.net"
    if domain == "":
        print("ENV错误!")
        exit(0)
    url = domain + "/applyRecord/queryAppSynInfo"
    response_body = {}
    try:
        response = requests.request("POST", url, headers=request_header, json=request_body, timeout=3, verify=False)
        # JSON标准格式
        response_body = json.dumps(response.json(), ensure_ascii=False, indent=4)
        # print("响应:\n{}".format(response_body))
    except Exception as err:
        print(str(err))
        exit(0)
    response_json = json.loads(response_body)
    if response_json['code'] != '1000':
        return response_json['errorMsg']
    app = json.loads("{}")
    app['from'] = {
        'interfaceId': response_json['data']['fromInterfaceInfo']['id'],
        'systemCode': response_json['data']['fromInterfaceInfo']['systemCode']
    }
    app['toList'] = parse_to_list(response_json['data']['toInterfaceInfoList'])
    return app


def parse_to_list(source: list) -> list:
    result_list = []
    for item in source:
        item_json = item
        result_list.append({
            'interfaceId': item_json['interfaceRecord']['id'],
            'systemCode': item_json['interfaceRecord']['systemCode']
        })
    return result_list


def main():
    app_id_list = init_parse_app_config()
    env_list = ["BOE", "PRE", "PRD"]
    result_list = []
    for app_id in app_id_list:
        result = {}
        result['config'] = {}
        result['appId'] = app_id
        for env in env_list:
            result['config'][env] = query_app(app_id, env)
        result_list.append(result)
    print("---------App配置结果-----------")
    result_content = json.dumps(result_list, ensure_ascii=False, indent=4)
    result_file_name = os.path.expanduser(
        '~') + "/Library/Application Support/JetBrains/IntelliJIdea2021.3/scratches/ResponseBody.json"
    try:
        with open(result_file_name, 'w') as result_file_data:
            result_file_data.write(result_content)
    except Exception as e:
        print("创建[{}]文件失败, 请检查权限".format(result_file_name))
    print(json.dumps(result_list, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    main()
