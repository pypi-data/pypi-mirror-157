#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2022/6/21 15:59
# @Author  : xgy
# @Site    : 
# @File    : check.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
from loguru import logger

from csp.datatool.text_entity.check import EntityCheck


class SpoCheck(EntityCheck):
    
    def __init__(self, folder, output=None):
        super(SpoCheck, self).__init__(folder, output)

    def check_connections(self):
        """
        检查 connections.json
        """
        srcId_error_l = []
        categoryId_error_l = []
        self.get_sources_ids()
        self.get_conn_cate_ids()
        for index, item in enumerate(self.connections_data):
            if item["srcId"] not in self.src_ids:
                # srcId_error_l.append(item["srcId"])
                srcId_error_l.append([json.dumps(item, ensure_ascii=False), item["srcId"]])
            if item["categoryId"] not in self.conn_cate_ids:
                # categoryId_error_l.append(item["categoryId"])
                categoryId_error_l.append([json.dumps(item, ensure_ascii=False), item["categoryId"]])

        if srcId_error_l:
            save_path = os.path.join(self.output, "connections_srcid_error.txt") if self.output else "connections_srcid_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in srcId_error_l:
                    # fw.write(item + "\n")
                    fw.write(item[0] + "," + item[1] + "\n")
                logger.info("the result has been saved in {}".format(save_path))
        if categoryId_error_l:
            save_path = os.path.join(self.output, "connections_categoryid_error.txt") if self.output else "connections_categoryid_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in categoryId_error_l:
                    # fw.write(item + "\n")
                    fw.write(item[0] + "," + item[1] + "\n")
                logger.info("the result has been saved in {}".format(save_path))
        if not srcId_error_l and not categoryId_error_l:
            logger.info("the is no trouble in connections.json")

    def check_connectioncategory(self):
        """
        公共检查，connectioncategory.json 字段值为空
        :return:
        """
        connection_category_error_l = []
        # 检查字段全为空为空
        for item in self.connection_categories_data:
            if not item["id"] and not item["text"]:
                return False
            if item["id"] and not item["text"]:
                connection_category_error_l.append(item["id"])

        if connection_category_error_l:
            save_path = os.path.join(self.output, "connectioncategory_error.txt") if self.output else "connectioncategory_error.txt"
            with open(save_path, "w", encoding="utf-8") as fw:
                for item in connection_category_error_l:
                    fw.write(item + "\n")
                logger.info("the result has been saved in {}".format(save_path))
            return False
        else:
            logger.info("the is no trouble in connectioncategory.json")
            return True


def spo_check(folder, output=None):
    check_relation = SpoCheck(folder, output=output)
    check_relation.get_dataset()

    flag_sources = check_relation.check_sources()
    flag_labelcategory = check_relation.check_labelcategory()
    flag_connetioncategory = check_relation.check_connectioncategory()

    if flag_sources and flag_labelcategory and flag_connetioncategory:
        check_relation.check_labels()
        check_relation.check_connections()


if __name__ == '__main__':
    print("start")
