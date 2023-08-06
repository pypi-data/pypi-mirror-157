#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @desc: 常用工具
import json


def remove_special_chars(text):
    """
    去除特殊字符
    :param text:
    :return:
    """
    import re
    # text = re.sub('[a-zA-Z0-9!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘！[\\]^_`{|}~\s]+', "", text)
    text = re.sub('[!#$%&\'*./:;<=>?@?★‘！[\\]^`{|}~\s]+', "", text)
    text = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\xe5]+', '', text)
    return text.replace("　", "").replace("\n\r\t　", "").replace(",", "，").replace("\"", "")


def read_lines(file_path):
    """
    读取文件的lines
    :param file_path:
    :return:
    """
    with open(file_path, "r") as fp:
        return fp.readlines()


def read_lines_json(file_path):
    """
    读取文件的lines,并返回json列表
    :param file_path:
    :return:
    """
    with open(file_path, "r") as fp:
        return [
            json.loads(line)
            for line in fp.readlines()
        ]


def read_json(file_path):
    with open(file_path, "r") as f:
        return json.loads(f.read())


def write_lines(file_path, datas):
    with open(file_path, "w") as fp:
        for data in datas:
            fp.write(data)


def write_json_data(file_path, json_data):
    """
    写入
    :param file_path: 文件路径
    :param json_data: json数据
    :return:
    """
    with open(file_path, "w") as fp:
        fp.write(json.dumps(json_data, ensure_ascii=False, indent=4))


def download_file(url, store_path):
    """
    下载文件
    """
    print("start to download: " + url)
    import requests
    import os
    try:
        if os.path.exists(store_path):
            os.remove(store_path)
        res = requests.get(url.strip())
        # print("返回：" + str(res.status_code))
        if res.status_code != 200:
            print("下载失败：" + str(res.status_code))
            return False
        with open(store_path, 'wb') as file:
            file.write(res.content)
            file.flush()
        print("download finish,save to:" + store_path)
        return True
    except Exception as  e:
        import sys
        print("download error:", e)
        return False
