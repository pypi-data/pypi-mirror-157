#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 15:02
# @Author  : xgy
# @Site    : 
# @File    : Kg.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import csp.aip.Kg
from csp.common.docker_server import DockerServer



class Kg:
    # 镜像版本号，默认值
    def_version = "1.0"
    # 镜像容器端口，默认值
    def_port = "30001"
    # 镜像名称，默认值
    def_name = "kg"

    def __init__(self, version=None, port=None, c_name=None, name=None, reload=True):
        if version:
            self.version = version
        else:
            self.version = self.def_version
        if port:
            self.port = port
        else:
            self.port = self.def_port
        if name:
            self.name = name
        else:
            self.name = self.def_name
        self.http_sdk = csp.aip.Kg(ip="127.0.0.1", port=self.port)

        # self.port = port
        self.server = DockerServer(name=self.name, version=self.version, port=self.port, c_name=c_name, reload=reload)
        self.server.start()
        # print("the kg ui at {}".format("http://127.0.0.1:" + self.port + "/components/kg/kgDeploy/kg-view.html"))

    def kg_create(self, class_file, code, link_file, name, node_file):
        """
        图谱创建
        """
        result = self.http_sdk.kg_create(class_file, code, link_file, name, node_file)

        return result

    def kg_list(self):
        """
        图谱列表
        """
        result = self.http_sdk.kg_list()
        print("kg ui url at {}".format(result["url"]))

        return result

    def kg_delete(self, ids):
        """
        图谱按id删除
        ids: 图谱id,以”,”相隔
        """
        result = self.http_sdk.kg_delete(ids)

        return result


if __name__ == '__main__':
    print("start")

