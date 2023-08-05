#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/28 17:30
# @Author  : xgy
# @Site    : 
# @File    : kg_cli.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import click
from csp.command.cli import csptools
from csp.thirdparty import Kg

from csp.common.utils import format

# 一级命令 CSPtools kg
@csptools.group("kg")
def kg():
    """
    csp-cli kg Command line
    """

## 创建图谱
@kg.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option("-d", "--class_file", help="the design csv path", required=True)
@click.option("-l", "--link_file", help="the relation csv path", required=True)
@click.option("-e", "--node_file", help="the entity csv path", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-c", "--code", help="the identifier of kg", required=True)
@click.option("-n", "--name", help="the name of kg", required=True)
def kg_create(version, port, c_name, r, class_file, link_file, node_file, code, name):
    """
    csp-cli kg extract_text line
    """
    unst2st = Kg(version=version, port=port, c_name=c_name, reload=r)
    result = unst2st.kg_create(class_file, code, link_file, name, node_file)


# 图谱列表
@kg.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
def kg_list(version, port, c_name, r):
    kg = Kg(version=version, port=port, c_name=c_name, reload=r)
    result = kg.kg_list()
    title_dict = {"id": "id", "图谱名称": 'kgName', "图谱标识符": 'kgCode', "图谱描述": 'kgDesc', "创建者": 'creator',
                  "创建时间": "createTime"}

    res_dict = {"data": result['records']}
    format(res_dict, title_dict)


# 图谱删除
@kg.command()
@click.option("-v", "--version", help="the version of server images", default=None)
@click.option("-p", "--port", help="the port for server container", default=None)
@click.option("-c", "--c_name", help="the container name", default=None)
@click.option('-r', is_flag=True, help="Re query image information.Indicates true when it appears")
@click.option("-i", "--ids", help="the ids will be deleted. Multiple IDs are separated by commas", required=True)
def kg_delete(version, port, c_name, r, ids):
    kg = Kg(version=version, port=port, c_name=c_name, reload=r)
    result = kg.kg_delete(ids)


if __name__ == '__main__':
    print("start")
