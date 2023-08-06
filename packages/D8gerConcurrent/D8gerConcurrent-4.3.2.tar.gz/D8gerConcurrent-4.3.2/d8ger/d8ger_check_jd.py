#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import os
import ssl

import requests

"""
读取cookie文件
读取搜索条件文件
解析搜索结果数据
查询单条数据，获得内推TOKEN数据
查询内推短链
保存岗位数据结果
"""
# 屏蔽HTTPS证书校验, 忽略安全警告
requests.packages.urllib3.disable_warnings()
context = ssl._create_unverified_context()

header_file_path = os.path.expanduser('~') + "/JD-POST/session-bytedance-cookie-read-only.json"
check_job_file_path = os.path.expanduser('~') + "/JD-POST/JobID.txt"


def execute_jd_post() -> str:
    """
    自动登录, 获取登录Cookie
    :rtype: str
    """
    header_json = json.loads("{}")
    try:
        with open(header_file_path, 'r') as header_data:
            header_json = json.load(header_data)
    except Exception as e:
        print("header_json数据解析错误")
        exit(0)
    job_id_list = []
    try:
        with open(check_job_file_path, 'r') as check_job_data:
            for line in check_job_data:
                job_id_list.append(line.strip("\n"))
    except Exception as e:
        print("header_json数据解析错误")
        exit(0)
    # 0: 社招  1: 校招
    is_not_campus = (header_json['jd-type'] == "0")
    print(".........查询[{}岗位]........".format("社招" if is_not_campus else "校招"))
    print("header_json: {}\n".format(json.dumps(header_json, ensure_ascii=False, indent=4)))
    query_json = {
      "offset": 0,
      "limit": 1,
      "key_words": "X4TV"
    }
    for id in job_id_list:
        query_json['key_words'] = id
        # 第一步查列表
        try:
            first_query_url = "https://people.bytedance.net/atsx/api/referral/job/posts/" if is_not_campus else "https://people.bytedance.net/atsx/api/referral/campus/job/posts/"
            job_post_info_list = query_first(first_query_url, header_json, query_json)
            if len(job_post_info_list) == 0:
                print("-WARN-岗位ID {} 查无此岗!".format(id))
                continue
            for item in job_post_info_list:
                item_json = item
                job_uniq_code = item_json['code']
                if item_json['channel_online_status'] != 1:
                    print("-ERROR-岗位ID {} 已经停招! channel_online_status={}".format(job_uniq_code, item_json['channel_online_status']))
                else:
                    print("岗位ID {} 招聘状态OK channel_online_status={}".format(job_uniq_code, item_json['channel_online_status']))
        except Exception as e:
            print("[{}]查询岗位列表错误!".format(id), e)
            exit(0)


def query_first(first_query_url: str, header_json: json, query_json:json) -> list:
    try:
        query_response = requests.request("POST", first_query_url, headers=header_json, json=query_json, timeout=3,
                                          verify=False)
        if query_response.status_code is None or query_response.status_code != 200:
            print("查询岗位列表失败, token可能已过期!")
        # JSON标准格式
        query_response_body = json.dumps(query_response.json(), ensure_ascii=False, indent=4)
        first_result = json.loads(query_response_body)
        return first_result['data']['job_post_info_list']
    except Exception as e:
        print("[{}]查询岗位列表错误!".format(id), e)
        exit(0)


def main():
    execute_jd_post()


if __name__ == '__main__':
    main()
