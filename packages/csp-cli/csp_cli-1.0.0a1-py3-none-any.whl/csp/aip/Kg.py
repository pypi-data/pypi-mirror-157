#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 15:04
# @Author  : xgy
# @Site    : 
# @File    : PdfCheck.py
# @Software: PyCharm
# @python version: 3.7.4
"""

from .common.http_client import HttpClient


class Kg:
    # 镜像版本号，默认值
    def_version = "1.0"
    # 镜像容器端口，默认值
    def_port = "30001"
    # 镜像名称，默认值
    def_name = "kg"

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def kg_create(self, class_file, code, link_file, name, node_file):
        """
        图谱构建
        """
        http_client = HttpClient()
        # url = "http://127.0.0.1:" + str(self.port) + "/kgExtension/createKg"
        url = "http://" + self.ip + ":" + str(self.port) + "/kgExtension/createKg"

        files = {
            "classFile": open(class_file, 'rb'),
            "linkFile": open(link_file, 'rb'),
            "nodeFile": open(node_file, 'rb')
        }
        data = {"name": name, "code": code}
        params = {"files": files, "data": data}
        dt = http_client.post(url, arg_type="data/files", **params)

        kg_url = dt["data"]
        print("the kg has been create successful at {}".format("http://" + self.ip + ":" + str(self.port) + kg_url))
        return kg_url

    def kg_list(self):
        """
        图谱列表查询
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/kgInfo/lists"

        dt = http_client.get(url)

        result = dt["data"]
        result["url"] = "http://" + self.ip + ":" + str(self.port) + result["url"]

        return result

    def kg_delete(self, ids):
        """
        图谱列表查询
        """
        http_client = HttpClient()
        url = "http://" + self.ip + ":" + str(self.port) + "/kgInfo/delete"

        data = {"ids": ids}

        dt = http_client.post(url, arg_type="data", **data)

        result = dt["data"]
        print("delete kg {} successful".format(ids))

        return result


if __name__ == '__main__':
    print("start")


