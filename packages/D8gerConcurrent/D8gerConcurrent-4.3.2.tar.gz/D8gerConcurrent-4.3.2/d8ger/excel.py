#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

header_file_path = os.path.expanduser('~') + "/JD-POST/session-bytedance-cookie-read-only.json"
query_file_path = os.path.expanduser('~') + "/JD-POST/bytedanceRequestBody.json"
jd_post_file_path = os.path.expanduser('~') + "/JD-POST/bytedanceResponseBody.json"
jd_excel_file_path = os.path.expanduser('~') + "/JD-POST/OJ8K.xlsx"
test_excel_file_path = os.path.expanduser('~') + "/JD-POST/hyperlink.xlsx"


def main():
    jd_dict = json.loads("{}")
    try:
        with open(jd_post_file_path, 'r') as json_data:
            jd_dict = json.load(json_data)
    except Exception as e:
        print("jd_json数据解析错误")
        exit(0)
    jd_json = json.dumps(jd_dict['list'])
    data_frame = pd.read_json(jd_json, encoding="utf-8", orient='records')
    data_frame['jobHotFlag'] = data_frame['jobHotFlag'].apply(lambda x: str(x))
    data_frame['jobId'] = data_frame['jobId'].apply(lambda x: str(x))
    # 设置数据超链接
    hyperlink_list = []
    for short_link, name in zip(data_frame['jobShortLink'], data_frame['jobName']):
        hyperlink_list.append("=HYPERLINK({}, {})".format(short_link, name))
    data_frame.style.format({'jobId': 'object'})
    print(data_frame)
    workbook = None
    try:
        workbook = xlsxwriter.Workbook(jd_excel_file_path)
        worksheet = workbook.add_worksheet('字节跳动-飞书内推-帝八哥')
        worksheet.set_column('A:O', 20)
        # 列标题
        columns = list(data_frame)
        for column_name in columns:
            worksheet.write(0, columns.index(column_name), column_name)
        # 行数据遍历
        for row_index in data_frame.index:
            column_data = data_frame.iloc[row_index]
            for column_name in columns:
                if column_name == 'jobName':
                    # 超链接
                    worksheet.write_url(row_index + 1, columns.index(column_name), column_data['jobShortLink'], string=column_data['jobName'])
                else:
                    worksheet.write(row_index + 1, columns.index(column_name), column_data[column_name])
    finally:
        if workbook is not None:
            workbook.close()


    #
    # # Add a sample alternative link format.
    # red_format = workbook.add_format({
    #     'font_color': 'red',
    #     'bold': 1,
    #     'underline': 1,
    #     'font_size': 12,
    # })
    #
    # # Write some hyperlinks
    # worksheet.write_url('A1', 'http://www.python.org/')  # Implicit format.
    # worksheet.write_url('A3', 'http://www.python.org/', string='Python Home')
    # worksheet.write_url('A5', 'http://www.python.org/', tip='Click here')
    # worksheet.write_url('A7', 'http://www.python.org/', red_format)
    # worksheet.write_url('A9', 'mailto:jmcnamara@cpan.org', string='Mail me')



if __name__ == '__main__':
    main()
