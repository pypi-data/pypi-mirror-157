#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import json
import os
import ssl
import pandas as pd
import xlsxwriter

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

# 文件目录
home_path = os.path.expanduser('~') + "/JD-POST"
# 请求头文件
header_file_path = home_path + "/session-bytedance-cookie-read-only.json"
# 查询请求参数文件
query_file_path = home_path + "/bytedanceRequestBody.json"
# 处理结果文件
jd_post_file_path = home_path + "/bytedanceResponseBody.json"
# 查询岗位个数限制
max_limit = 7000


def execute_jd_post():
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
    query_json = json.loads("{}")
    try:
        with open(query_file_path, 'r') as query_data:
            query_json = json.load(query_data)
    except Exception as e:
        print("query_json数据解析错误")
        exit(0)
    print("header_json: {}\nquery_json: {}".format(json.dumps(header_json, ensure_ascii=False, indent=4), json.dumps(query_json, ensure_ascii=False, indent=4)))
    # 第一步查列表
    first_job_list_result = []
    count = 0
    real_num = 0
    # 0: 社招  1: 校招
    is_not_campus = (header_json['jd-type'] == "0")
    global max_limit
    if header_json['max-limit'] is not None and header_json['max-limit'].isdigit():
        max_limit = int(header_json['max-limit'])
    print("...........查询[{}岗位], 限制查询数量[{}]...........".format("社招" if is_not_campus else "校招", max_limit))
    try:
        first_query_url = "https://people.bytedance.net/atsx/api/referral/job/posts/" if is_not_campus else "https://people.bytedance.net/atsx/api/referral/campus/job/posts/"
        first_result = query_first(first_query_url, header_json, query_json)
        count = first_result['count']
        job_post_info_list = first_result['job_post_info_list']
        if (count is None) or count <= 0:
            print("查询岗位数据为空!")
            exit(0)
        print("...........查询岗位total={}, real_num={}...........".format(count, len(job_post_info_list)))
        first_job_list_result = parse_to_list(job_post_info_list)
    except Exception as e:
        print("查询岗位列表错误!", e)
        exit(0)
    result = json.loads("{}")
    result['count'] = count
    result['real_num'] = real_num
    result['list'] = fetch_short_link(first_job_list_result, header_json)
    # 写JSON
    try:
        with open(jd_post_file_path, 'w') as jd_post_file_data:
            jd_post_file_data.write(json.dumps(result, ensure_ascii=False, indent=4))
    except Exception as e:
        print("解析结果保存出错! {}".format(e))
    # 生成excel
    excel_file_path = "{}{}".format(home_path, "/字节跳动-飞书内推-帝八哥.xlsx")
    generate_excel(result, excel_file_path)
    print("解析结果已存入: [{}], excel文件: [{}]".format(jd_post_file_path, excel_file_path))


def query_first(first_query_url: str, header_json: json, query_json: json) -> json:
    current_offset = query_json['offset']
    print("...........首次查询offset={}, limit={}..............".format(current_offset, query_json['limit']))
    result = execute_query_page(first_query_url, header_json, query_json)
    total = result['count']
    current_offset = current_offset + len(result['job_post_info_list'])
    while (current_offset < total) and (len(result['job_post_info_list']) < max_limit):
        # 暂停50ms
        time.sleep(0.05)
        query_json['offset'] = current_offset
        print("...........分页查询offset={}, total={}, limit={}..............".format(current_offset, total, query_json['limit']))
        item_result = execute_query_page(first_query_url, header_json, query_json)
        result['job_post_info_list'].extend(item_result['job_post_info_list'])
        current_offset = current_offset + len(item_result['job_post_info_list'])
    return result


def execute_query_page(first_query_url: str, header_json: json, query_json: json) -> json:
    try:
        query_response = requests.request("POST", first_query_url, headers=header_json, json=query_json, timeout=3,
                                          verify=False)
        if query_response.status_code is None or query_response.status_code != 200:
            print("查询岗位列表失败, token可能已过期!")
        # JSON标准格式
        query_response_body = json.dumps(query_response.json(), ensure_ascii=False, indent=4)
        first_result = json.loads(query_response_body)
        result = {
            "count": first_result['data']['count'],
            "job_post_info_list": first_result['data']['job_post_info_list']
        }
        return result
    except Exception as e:
        print("[{}]查询岗位列表错误!".format(id), e)
        exit(0)


def fetch_short_link(source: list, header_json: json) -> list:
    result_list = []
    # 0: 社招  1: 校招
    is_not_campus = (header_json['jd-type'] == "0")
    i = 1
    for item in source:
        # 暂停50ms
        time.sleep(0.05)
        item_json = item
        if is_not_campus:
            try:
                get_url = "https://people.bytedance.net/atsx/api/referral/job/posts/{}/".format(item_json['jobId'])
                get_item_response = requests.request("GET", get_url, headers=header_json, timeout=3, verify=False)
                # JSON标准格式
                get_item_response_body = json.dumps(get_item_response.json(), ensure_ascii=False, indent=4)
                second_item_result = json.loads(get_item_response_body)
                item_token = second_item_result['data']['job_post_info']['share_info']['token']
                item_url = "https://job.toutiao.com/referral/pc/position/detail/?token={}".format(item_token)
            except Exception as e:
                print("查询JD详情错误!", e)
                continue
        else:
            item_url = "https://jobs.toutiao.com/campus/position/detail/{}?referral_code=NF69Y61".format(item_json['jobId'])
        third_short_request_json = {
            "url": item_url
        }
        try:
            post_item_response = requests.request("POST",
                                                  "https://people.bytedance.net/atsx/api/common/snssdk/shortpath",
                                                  headers=header_json, json=third_short_request_json, timeout=3,
                                                  verify=False)
            post_item_response_body = json.dumps(post_item_response.json(), ensure_ascii=False, indent=4)
            last_item_result = json.loads(post_item_response_body)
            short_link = last_item_result['data']['short_url']
        except Exception as e:
            print("获取内推短链错误!", e)
            continue
        print("[{0:>5}] {1:>8} {2:>35}  {3}".format(i, item_json['jobUniqCode'], short_link, item_json['jobName']))
        result_list.append(load_result(item_json, short_link))
        i = i + 1
    return result_list


def load_result(item_json: json, short_link: str) -> json:
    result = {
        'jobCityName': item_json['jobCityName'],
        'jobName': item_json['jobName'],
        'jobUniqCode': item_json['jobUniqCode'],
        'jobOnlineStatus': item_json['jobOnlineStatus'],
        'jobType': item_json['jobType'],
        'jobSubType': item_json['jobSubType'],
        'jobDepartment': item_json['jobDepartment'],
        'jobRecruitType': item_json['jobRecruitType'],
        'jobRecruitLevel': item_json['jobRecruitLevel'],
        'jobHotFlag': item_json['jobHotFlag'],
        'jobId': item_json['jobId'],
        'jobCityCode': item_json['jobCityCode'],
        'jobPublishTime': item_json['jobPublishTime'],
        'jobShortLink': short_link
    }
    return result


def check_data(item_json: json) -> bool:
    if (item_json['city_info'] is None) or (item_json['city_info']['name'] is None) or (item_json['city_info']['code'] is None):
        return False
    if (item_json['department'] is None) or (item_json['department']['name'] is None):
        return False
    if (item_json['job_category'] is None) or (item_json['job_category']['name'] is None):
        return False
    if (item_json['recruit_type'] is None) or (item_json['recruit_type']['name'] is None):
        return False
    if (item_json['recruit_type']['parent'] is None) or (item_json['recruit_type']['parent']['name'] is None):
        return False
    return True


def parse_to_list(source: list) -> list:
    result_list = []
    for item in source:
        item_json = item
        if not check_data(item_json):
            print("缺失数据: \n\t{}".format(json.dumps(item_json, ensure_ascii=False, indent=4)))
            continue
        item_result = {
            'jobCityName': item_json['city_info']['name'],
            'jobName': item_json['name'],
            'jobUniqCode': item_json['code'],
            'jobOnlineStatus': "否" if item_json['channel_online_status'] == 1 else "是",
            'jobDepartment': item_json['department']['name'],
            'jobSubType': item_json['job_category']['name'],
            'jobRecruitLevel': item_json['recruit_type']['name'],
            'jobRecruitType': item_json['recruit_type']['parent']['name'],
            'jobHotFlag': "急招" if item_json['job_hot_flag'] == 1 else "热招",
            'jobId': item_json['id'],
            'jobCityCode': item_json['city_info']['code'],
            'jobPublishTime': publish_time_format(item_json['publish_time'])
        }
        job_type_parent = item_json['job_category']['parent']
        if (job_type_parent is not None) and (job_type_parent['name'] is not None):
            item_result['jobType'] = job_type_parent['name']
        else:
            item_result['jobType'] = item_json['job_category']['name']
        result_list.append(item_result)
    return result_list


def publish_time_format(timestamp: str) -> str:
    time_array = time.localtime(int(timestamp) / 1000)
    return time.strftime("%Y-%m-%d %H:%M:%S", time_array)


def generate_excel(source: json, file_name: str):
    jd_json = json.dumps(source['list'])
    data_frame = pd.read_json(jd_json, encoding="utf-8", orient='records')
    data_frame['jobId'] = data_frame['jobId'].apply(lambda x: str(x))
    workbook = None
    try:
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet('字节跳动-飞书内推-帝八哥')
        worksheet.set_column('A:O', 20)
        # 列标题
        header_title = {
            "jobCityName": "城市",
            "jobCityCode": "城市编码",
            "jobName": "岗位名称",
            "jobShortLink": "内推链接",
            "jobUniqCode": "岗位ID",
            "jobType": "序列",
            "jobSubType": "子序列",
            "jobDepartment": "部门",
            "jobRecruitType": "社招/校招",
            "jobRecruitLevel": "正式/实习",
            "jobOnlineStatus": "是否停招",
            "jobHotFlag": "招聘热度",
            "jobId": "序列号",
            "jobPublishTime": "发布日期",
        }
        columns = list(data_frame)
        excel_remove_short_url = True
        for column_name in columns:
            if excel_remove_short_url and column_name == "jobShortLink":
                continue
            worksheet.write(0, columns.index(column_name), header_title.get(column_name, "开赴火星"))
        # 行数据遍历
        for row_index in data_frame.index:
            column_data = data_frame.iloc[row_index]
            for column_name in columns:
                if excel_remove_short_url and column_name == "jobShortLink":
                    continue
                if column_name == 'jobName':
                    view_name = column_data['jobName'] + "[☆]" if ("飞书" in column_data['jobName']) else column_data['jobName']
                    # 超链接
                    worksheet.write_url(row_index + 1, columns.index(column_name), column_data['jobShortLink'], string=view_name)
                else:
                    worksheet.write(row_index + 1, columns.index(column_name), column_data[column_name])
    finally:
        if workbook is not None:
            workbook.close()


def main():
    execute_jd_post()


if __name__ == '__main__':
    main()
